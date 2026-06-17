"""Polymarket Source — real prediction-market odds for finance.

Polymarket is a prediction market: traders buy/sell shares of "Yes"/"No" on
real-world events, so a market's price *is* a crowd-sourced probability. That is
exactly what Ghost tries to estimate heuristically elsewhere — here we get the
real number, traded with real money.

This source pulls the most active finance/crypto/macro markets from Polymarket's
public Gamma API (no key required), keeping the implied probability, 24h price
move, and volume in metadata so `signals.py` can turn each into a first-class
prediction signal.
"""
import json
import re
from datetime import datetime
from typing import AsyncIterator

import httpx

from config import (
    POLYMARKET_ENABLED,
    POLYMARKET_GAMMA_URL,
    POLYMARKET_MAX_MARKETS,
    POLYMARKET_KEYWORDS,
)
from .base import BaseSource, ContentItem


class PolymarketSource(BaseSource):
    """Fetch trending finance prediction markets from Polymarket."""

    name = "polymarket"

    def __init__(self):
        self.base_url = POLYMARKET_GAMMA_URL.rstrip("/")
        # Precompiled keyword patterns. We use "not surrounded by alphanumerics"
        # boundaries so short tokens (fed, oil, eth) don't match inside unrelated
        # words ("federation", "boil", "ethics") — that false-positive flooded the
        # feed with sports/politics markets in testing.
        self._patterns = [
            re.compile(r'(?<![a-z0-9])' + re.escape(kw) + r'(?![a-z0-9])')
            for kw in POLYMARKET_KEYWORDS
        ]

    async def is_configured(self) -> bool:
        # Public API — only gated by the feature flag.
        return POLYMARKET_ENABLED

    async def fetch(self, limit: int = 50) -> AsyncIterator[ContentItem]:
        if not await self.is_configured():
            print("Polymarket disabled (POLYMARKET_ENABLED=false), skipping")
            return

        try:
            markets = await self._fetch_markets()
        except Exception as e:
            print(f"Polymarket fetch failed: {e}")
            return

        relevant = [m for m in markets if self._is_finance(m)]
        # Most actively traded first.
        relevant.sort(key=lambda m: self._as_float(m.get("volume24hr")), reverse=True)

        cap = min(limit, POLYMARKET_MAX_MARKETS)
        count = 0
        for market in relevant:
            item = self._to_content_item(market)
            if not item:
                continue
            yield item
            count += 1
            if count >= cap:
                break

    async def _fetch_markets(self) -> list[dict]:
        params = {
            "active": "true",
            "closed": "false",
            "archived": "false",
            "order": "volume24hr",
            "ascending": "false",
            "limit": "500",
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(f"{self.base_url}/markets", params=params)
            response.raise_for_status()
            data = response.json()
        if isinstance(data, dict):
            data = data.get("data", data.get("markets", []))
        return data if isinstance(data, list) else []

    def _is_finance(self, market: dict) -> bool:
        # Match against the question/category/slug only — the description is long
        # and noisy (an Iran market mentioning "oil", a World Cup market mentioning
        # "Federation") and produces false positives.
        haystack = " ".join(
            str(market.get(k, "")) for k in ("question", "category", "slug")
        ).lower()
        return any(p.search(haystack) for p in self._patterns)

    def _to_content_item(self, market: dict) -> ContentItem | None:
        question = market.get("question") or market.get("title")
        if not question:
            return None

        outcomes = self._parse_json_field(market.get("outcomes"))
        prices = [self._as_float(p) for p in self._parse_json_field(market.get("outcomePrices"))]
        implied_prob, top_outcome = self._implied_probability(outcomes, prices)

        volume_24h = self._as_float(market.get("volume24hr"))
        volume = self._as_float(market.get("volume") or market.get("volumeNum"))
        liquidity = self._as_float(market.get("liquidity") or market.get("liquidityNum"))
        one_day_change = self._as_float(market.get("oneDayPriceChange"))

        url = self._market_url(market)
        description = (market.get("description") or "")[:1500]

        odds_summary = ", ".join(
            f"{o}: {round(p * 100)}%" for o, p in zip(outcomes, prices)
        ) if outcomes and prices else ""

        content = "\n".join(filter(None, [
            question,
            description,
            f"Market odds — {odds_summary}" if odds_summary else "",
            f"24h volume: ${volume_24h:,.0f}" if volume_24h else "",
        ]))[:3000]

        return ContentItem(
            source="polymarket",
            source_id=str(market.get("id") or market.get("slug") or question),
            title=question,
            content=content,
            url=url,
            author="Polymarket",
            engagement=int(volume_24h),
            # Prediction markets stay open for months, so the market's start date is
            # not "freshness". Stamp with scrape time so the recency window reflects
            # when we last saw this market trending; keep the real dates in metadata.
            published_at=datetime.utcnow(),
            metadata={
                "question": question,
                "description": description,
                "slug": market.get("slug", ""),
                "url": url,
                "implied_probability": round(implied_prob, 1),
                "top_outcome": top_outcome,
                "outcomes": outcomes,
                "outcome_prices": prices,
                "volume": volume,
                "volume_24h": volume_24h,
                "liquidity": liquidity,
                "one_day_price_change": one_day_change,
                "start_date": market.get("startDate", ""),
                "end_date": market.get("endDate", ""),
                "category": market.get("category", ""),
            },
        )

    @staticmethod
    def _implied_probability(outcomes: list, prices: list[float]) -> tuple[float, str]:
        """Return (probability %, outcome label) for the market's leading outcome.

        For a Yes/No market this is the price of 'Yes'. For multi-outcome markets
        it's the highest-priced outcome.
        """
        if not prices:
            return 0.0, ""
        if outcomes and "yes" in [str(o).lower() for o in outcomes]:
            yes_idx = [str(o).lower() for o in outcomes].index("yes")
            return prices[yes_idx] * 100, "Yes"
        top_idx = max(range(len(prices)), key=lambda i: prices[i])
        label = outcomes[top_idx] if top_idx < len(outcomes) else ""
        return prices[top_idx] * 100, label

    def _market_url(self, market: dict) -> str:
        events = market.get("events")
        if isinstance(events, list) and events and isinstance(events[0], dict):
            slug = events[0].get("slug")
            if slug:
                return f"https://polymarket.com/event/{slug}"
        slug = market.get("slug")
        if slug:
            return f"https://polymarket.com/event/{slug}"
        return "https://polymarket.com"

    @staticmethod
    def _parse_json_field(value):
        """Gamma returns outcomes/prices as JSON-encoded strings (or plain lists)."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                return []
        return []

    @staticmethod
    def _as_float(value) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _parse_date(value) -> datetime:
        if not value:
            return datetime.utcnow()
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
        except (ValueError, AttributeError):
            return datetime.utcnow()
