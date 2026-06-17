"""
Tests for the Polymarket source + prediction-market signal generation.

These are network-free: they feed a representative Gamma-API market dict through
the parsing/signal-building logic, so they're deterministic and fast.

Run from the `scraper/` directory:
    pytest tests/test_prediction_markets.py
"""
import asyncio
import json
import os
import tempfile

import pytest

from sources.polymarket import PolymarketSource
from database import Database
from signals import SignalGenerator


# A trimmed-down but realistic Gamma /markets item. Note: outcomes/prices come
# back as JSON-encoded strings, which is the shape that bit us in testing.
SAMPLE_MARKET = {
    "id": "0x123",
    "question": "Will the Fed cut interest rates at its next meeting?",
    "description": "Resolves YES if the Federal Reserve lowers the target rate.",
    "slug": "fed-rate-cut-next-meeting",
    "outcomes": json.dumps(["Yes", "No"]),
    "outcomePrices": json.dumps(["0.38", "0.62"]),
    "volume24hr": "2480000",
    "volume": "9100000",
    "liquidity": "550000",
    "oneDayPriceChange": "0.06",
    "startDate": "2026-01-01T00:00:00Z",
    "endDate": "2026-07-30T00:00:00Z",
    "category": "Economy",
    "events": [{"slug": "fed-decision-2026"}],
}


def test_finance_filter_keeps_finance_rejects_sports():
    src = PolymarketSource()
    assert src._is_finance(SAMPLE_MARKET) is True
    # "Federation" must NOT match the "fed" keyword (word-boundary guard).
    assert src._is_finance({
        "question": "Will Mexico win the 2026 FIFA World Cup?",
        "category": "Sports",
        "slug": "world-cup-winner",
    }) is False


def test_to_content_item_parses_odds():
    src = PolymarketSource()
    item = src._to_content_item(SAMPLE_MARKET)
    assert item is not None
    assert item.source == "polymarket"
    meta = item.metadata
    # Yes price 0.38 -> 38% implied probability
    assert meta["implied_probability"] == pytest.approx(38.0, abs=0.1)
    assert meta["top_outcome"] == "Yes"
    assert meta["volume_24h"] == pytest.approx(2_480_000)
    assert meta["url"] == "https://polymarket.com/event/fed-decision-2026"


def test_implied_probability_picks_yes_then_max():
    src = PolymarketSource()
    # Binary Yes/No -> probability of "Yes"
    prob, label = src._implied_probability(["Yes", "No"], [0.38, 0.62])
    assert label == "Yes" and prob == pytest.approx(38.0)
    # Multi-outcome -> highest priced outcome
    prob, label = src._implied_probability(["A", "B", "C"], [0.2, 0.5, 0.3])
    assert label == "B" and prob == pytest.approx(50.0)


def test_prediction_signal_end_to_end():
    async def run():
        tmp = os.path.join(tempfile.mkdtemp(), "pred.db")
        db = Database(tmp)
        await db.init()

        item = PolymarketSource()._to_content_item(SAMPLE_MARKET)
        await db.save_content(item.to_dict())

        # Metadata must survive the SQLite round-trip as a dict.
        from datetime import datetime, timedelta
        rows = await db.get_platform_content("polymarket", since=datetime.utcnow() - timedelta(days=7))
        assert len(rows) == 1
        assert isinstance(rows[0]["metadata"], dict)

        sg = SignalGenerator(db)
        sg.client = None  # force templated insight, no API calls
        signals = await sg.generate_prediction_market_signals(datetime.utcnow() - timedelta(days=7))
        assert len(signals) == 1

        s = signals[0]
        assert s["marketType"] == "prediction"
        assert s["eventProbability"] == 38          # real traded odds, not a heuristic
        assert s["impliedProbability"] == 38
        assert s["change24h"] == pytest.approx(6.0)  # 0.06 * 100 points
        assert s["marketVolume24h"] == 2_480_000
        assert s["marketUrl"].startswith("https://polymarket.com/")
        # Fed market should map to rate proxies
        symbols = [t["symbol"] for t in s["relatedTickers"]]
        assert "TLT" in symbols and "SPY" in symbols
        assert len(s["velocityData"]) == 15

    asyncio.run(run())


def test_question_ticker_mapping_is_conservative():
    sg = SignalGenerator.__new__(SignalGenerator)  # no DB needed for this helper
    assert "IBIT" in sg._map_question_to_tickers("Will Bitcoin hit $150k?")
    assert sg._map_question_to_tickers("Will it rain in Seattle tomorrow?") == []
