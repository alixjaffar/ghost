"""
Signal Generation for Ghost

This module transforms raw scraped content and ticker mentions into
actionable signals with probability, acceleration, and confidence scores.
"""
import asyncio
import re
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional
import anthropic

from config import (
    ANTHROPIC_API_KEY, BULK_MODEL, INSIGHT_MODEL,
    QUESTION_TICKER_MAP, TRACKED_TICKERS,
)
from database import Database
from models import Platform, Sentiment


class SignalGenerator:
    """Generates Ghost signals from raw scraped data."""
    
    def __init__(self, db: Database):
        self.db = db
        self.client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
    
    async def generate_all_signals(self) -> list[dict]:
        """Generate signals from all recent data."""
        # Get data from last 7 days
        cutoff = datetime.utcnow() - timedelta(days=7)
        
        # Get all ticker mentions
        mentions = await self.db.get_recent_mentions(since=cutoff)
        
        # Group by potential narratives (cluster tickers that appear together)
        narratives = await self._cluster_narratives(mentions)
        
        # Generate signal for each narrative
        signals = []
        for narrative in narratives:
            signal = await self._generate_signal(narrative)
            if signal:
                signals.append(signal)

        # Add first-class prediction-market signals (real traded odds)
        try:
            prediction_signals = await self.generate_prediction_market_signals(cutoff)
            signals.extend(prediction_signals)
        except Exception as e:
            print(f"Prediction-market signal generation failed: {e}")

        # Sort by acceleration score
        signals.sort(key=lambda x: x['accelerationScore'], reverse=True)

        return signals
    
    async def _cluster_narratives(self, mentions: list[dict]) -> list[dict]:
        """Cluster ticker mentions into narratives."""
        # Simple clustering: group by co-occurring tickers in same content
        content_tickers = defaultdict(set)
        ticker_content = defaultdict(list)
        
        for mention in mentions:
            content_id = mention.get('content_id')
            ticker = mention.get('ticker')
            if content_id and ticker:
                content_tickers[content_id].add(ticker)
                ticker_content[ticker].append(mention)
        
        # Find ticker groups that appear together
        ticker_cooccurrence = defaultdict(lambda: defaultdict(int))
        for content_id, tickers in content_tickers.items():
            for t1 in tickers:
                for t2 in tickers:
                    if t1 != t2:
                        ticker_cooccurrence[t1][t2] += 1
        
        # Build narratives from strongly co-occurring tickers
        used_tickers = set()
        narratives = []
        
        # Sort tickers by total mentions
        ticker_volumes = {t: len(mentions) for t, mentions in ticker_content.items()}
        sorted_tickers = sorted(ticker_volumes.keys(), key=lambda x: ticker_volumes[x], reverse=True)
        
        for primary_ticker in sorted_tickers:
            if primary_ticker in used_tickers:
                continue
            
            # Find related tickers
            related = [primary_ticker]
            for other, count in ticker_cooccurrence[primary_ticker].items():
                if other not in used_tickers and count >= 3:  # At least 3 co-occurrences
                    related.append(other)
            
            if len(related) >= 1:  # Need at least the primary ticker
                used_tickers.update(related)
                narratives.append({
                    'tickers': related[:5],  # Max 5 tickers per narrative
                    'mentions': [m for t in related for m in ticker_content[t]],
                })
        
        return narratives[:20]  # Max 20 narratives
    
    async def _generate_signal(self, narrative: dict) -> Optional[dict]:
        """Generate a signal from a narrative cluster."""
        tickers = narrative['tickers']
        mentions = narrative['mentions']
        
        if not mentions:
            return None
        
        # Calculate basic metrics
        total_mentions = len(mentions)
        
        # Calculate sentiment distribution
        sentiment_counts = defaultdict(int)
        for m in mentions:
            sentiment_counts[m.get('sentiment', 'neutral')] += 1
        
        # Calculate platform breakdown
        platform_counts = defaultdict(int)
        for m in mentions:
            platform_counts[m.get('platform', 'unknown')] += 1
        
        # Calculate velocity (mentions over time)
        now = datetime.utcnow()
        recent_24h = sum(1 for m in mentions 
                        if datetime.fromisoformat(m['created_at'].replace('Z', '+00:00')).replace(tzinfo=None) > now - timedelta(hours=24))
        previous_24h = sum(1 for m in mentions
                         if now - timedelta(hours=48) < datetime.fromisoformat(m['created_at'].replace('Z', '+00:00')).replace(tzinfo=None) <= now - timedelta(hours=24))
        
        # Calculate 24h change
        if previous_24h > 0:
            change_24h = ((recent_24h - previous_24h) / previous_24h) * 100
        else:
            change_24h = 100 if recent_24h > 0 else 0
        
        # Calculate velocity data (last 14 days)
        velocity_data = []
        for days_ago in range(14, -1, -1):
            day_start = now - timedelta(days=days_ago+1)
            day_end = now - timedelta(days=days_ago)
            day_count = sum(1 for m in mentions
                          if day_start < datetime.fromisoformat(m['created_at'].replace('Z', '+00:00')).replace(tzinfo=None) <= day_end)
            velocity_data.append({
                'timestamp': day_end.isoformat(),
                'value': day_count
            })
        
        # Calculate scores
        acceleration_score = self._calculate_acceleration(velocity_data, change_24h)
        confidence = self._calculate_confidence(total_mentions, len(platform_counts))
        event_probability = self._calculate_probability(acceleration_score, confidence, change_24h)
        status = self._determine_status(acceleration_score, change_24h)
        
        # Get content samples for AI analysis
        content_samples = [m.get('context', '')[:500] for m in mentions[:10]]
        
        # Generate AI narrative (if client available)
        if self.client and content_samples:
            ai_result = await self._generate_ai_narrative(tickers, content_samples)
        else:
            ai_result = {
                'title': f"{tickers[0]} Narrative",
                'summary': f"Discussions around {', '.join(tickers)} are trending.",
                'fullDescription': f"Content mentioning {', '.join(tickers)} has been increasing across platforms.",
                'whyItMatters': "Monitor for potential market impact.",
                'aiInsight': "AI analysis unavailable - configure ANTHROPIC_API_KEY for insights."
            }
        
        # Build source breakdown
        source_breakdown = []
        for platform, count in sorted(platform_counts.items(), key=lambda x: x[1], reverse=True):
            source_breakdown.append({
                'platform': platform,
                'mentions': count,
                'percentChange24h': int(change_24h) if count > 0 else 0
            })
        
        # Build related tickers
        related_tickers = []
        bullish = sentiment_counts.get('bullish', 0)
        bearish = sentiment_counts.get('bearish', 0)
        
        for ticker in tickers:
            exposure = 'positive' if bullish > bearish else 'negative' if bearish > bullish else 'mixed'
            related_tickers.append({
                'symbol': ticker,
                'name': ticker,  # Would need ticker database for full names
                'exposure': exposure,
                'relevanceScore': 90 - (tickers.index(ticker) * 5)
            })
        
        # Build recent evidence
        recent_evidence = []
        for i, m in enumerate(sorted(mentions, key=lambda x: x['created_at'], reverse=True)[:5]):
            recent_evidence.append({
                'id': f"e{i}",
                'timestamp': m['created_at'],
                'platform': m.get('platform', 'unknown'),
                'title': m.get('title', '')[:100] or f"Discussion about {tickers[0]}",
                'snippet': m.get('context', '')[:200],
                'engagement': m.get('engagement', 0)
            })
        
        signal_id = '-'.join(tickers[:2]).lower()
        
        return {
            'id': signal_id,
            'title': ai_result['title'],
            'summary': ai_result['summary'],
            'fullDescription': ai_result['fullDescription'],
            'whyItMatters': ai_result['whyItMatters'],
            'eventProbability': event_probability,
            'accelerationScore': acceleration_score,
            'confidence': confidence,
            'status': status,
            'timeframeMin': 30,
            'timeframeMax': 90,
            'timeframeUnit': 'days',
            'change24h': round(change_24h, 1),
            'totalMentions': total_mentions,
            'relatedTickers': related_tickers,
            'sourceBreakdown': source_breakdown,
            'recentEvidence': recent_evidence,
            'velocityData': velocity_data,
            'aiInsight': ai_result['aiInsight'],
            'marketType': 'narrative',
            'createdAt': min(m['created_at'] for m in mentions),
            'updatedAt': datetime.utcnow().isoformat(),
        }
    
    def _calculate_acceleration(self, velocity_data: list, change_24h: float) -> int:
        """Calculate acceleration score 0-100."""
        if not velocity_data:
            return 0
        
        values = [v['value'] for v in velocity_data]
        
        # Recent vs historical average
        recent = sum(values[-3:]) / 3 if len(values) >= 3 else sum(values) / len(values)
        historical = sum(values[:-3]) / max(len(values) - 3, 1) if len(values) > 3 else recent
        
        if historical > 0:
            acceleration_ratio = recent / historical
        else:
            acceleration_ratio = 1 if recent == 0 else 2
        
        # Combine with 24h change
        score = min(100, max(0, int(
            (acceleration_ratio - 1) * 50 +  # Acceleration component
            min(change_24h, 100) * 0.3 +  # 24h change component
            30  # Base score
        )))
        
        return score
    
    def _calculate_confidence(self, total_mentions: int, platform_count: int) -> str:
        """Calculate confidence level based on data volume and diversity."""
        if total_mentions >= 1000 and platform_count >= 4:
            return 'very_high'
        elif total_mentions >= 500 and platform_count >= 3:
            return 'high'
        elif total_mentions >= 100 and platform_count >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_probability(self, acceleration: int, confidence: str, change_24h: float) -> int:
        """Calculate event probability estimate."""
        confidence_weights = {'very_high': 1.0, 'high': 0.8, 'medium': 0.6, 'low': 0.4}
        weight = confidence_weights.get(confidence, 0.5)
        
        # Base probability from acceleration
        base = acceleration * 0.6
        
        # Adjust for confidence
        adjusted = base * weight
        
        # Boost for very high 24h change
        if change_24h > 50:
            adjusted += 10
        
        return min(95, max(20, int(adjusted)))
    
    def _determine_status(self, acceleration: int, change_24h: float) -> str:
        """Determine signal status."""
        if acceleration >= 85 and change_24h >= 30:
            return 'breaking'
        elif acceleration >= 70 or change_24h >= 20:
            return 'accelerating'
        elif acceleration >= 50 or change_24h >= 0:
            return 'emerging'
        else:
            return 'cooling'
    
    async def _generate_ai_narrative(self, tickers: list, content_samples: list) -> dict:
        """Use AI to generate narrative title and summary."""
        prompt = f"""Analyze this social media content about the tickers {', '.join(tickers)} and generate a market narrative.

Content samples:
{chr(10).join(content_samples[:5])}

Respond with JSON only:
{{
  "title": "Short narrative title (3-6 words, not just ticker names)",
  "summary": "One sentence summary of what people are discussing",
  "fullDescription": "2-3 sentence detailed description of the narrative",
  "whyItMatters": "One sentence on potential market impact",
  "aiInsight": "2-3 sentence actionable insight for investors"
}}

Focus on the underlying story, not just that people are talking about the tickers."""

        try:
            response = await self.client.messages.create(
                model=BULK_MODEL,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            text = response.content[0].text
            # Extract JSON from response
            if '{' in text:
                json_str = text[text.find('{'):text.rfind('}')+1]
                return json.loads(json_str)
        except Exception as e:
            print(f"AI narrative generation failed: {e}")
        
        return {
            'title': f"{tickers[0]} Discussion Trending",
            'summary': f"Increased discussion around {', '.join(tickers)}",
            'fullDescription': f"Social media activity around {', '.join(tickers)} has been increasing.",
            'whyItMatters': "Monitor for potential market impact.",
            'aiInsight': "Unable to generate AI insight at this time."
        }

    # ===========================================
    # Prediction-market signals (Polymarket)
    # ===========================================

    async def generate_prediction_market_signals(self, cutoff: datetime) -> list[dict]:
        """Build first-class signals from Polymarket prediction markets.

        Unlike narrative signals, these carry a *real* traded probability as the
        event probability instead of a heuristic estimate.
        """
        rows = await self.db.get_platform_content('polymarket', since=cutoff)
        if not rows:
            return []

        # Dedupe by market slug/title, keeping the most recent snapshot.
        seen: set[str] = set()
        signals: list[dict] = []
        for row in rows:
            meta = row.get('metadata') or {}
            key = meta.get('slug') or row.get('title') or row.get('id')
            if key in seen:
                continue
            seen.add(key)
            signal = self._build_prediction_signal(row, meta)
            if signal:
                signals.append(signal)

        # Generate AI insights concurrently (falls back to the templated insight).
        if self.client and signals:
            insights = await asyncio.gather(
                *[self._generate_prediction_insight(s) for s in signals],
                return_exceptions=True,
            )
            for signal, insight in zip(signals, insights):
                if isinstance(insight, str) and insight:
                    signal['aiInsight'] = insight

        return signals

    def _build_prediction_signal(self, row: dict, meta: dict) -> Optional[dict]:
        question = meta.get('question') or row.get('title')
        if not question:
            return None

        prob = float(meta.get('implied_probability') or 0)
        prob_int = int(round(max(1, min(99, prob))))
        top_outcome = meta.get('top_outcome') or "this outcome"
        change_pts = round(float(meta.get('one_day_price_change') or 0) * 100, 1)
        volume_24h = float(meta.get('volume_24h') or 0)
        liquidity = float(meta.get('liquidity') or 0)
        url = meta.get('url') or row.get('url') or "https://polymarket.com"

        tickers = self._map_question_to_tickers(f"{question} {meta.get('description', '')}")

        accel = int(min(100, 30
                        + min(40, abs(change_pts) * 4)
                        + (30 if volume_24h >= 1_000_000 else 20 if volume_24h >= 250_000
                           else 10 if volume_24h >= 50_000 else 0)))

        if volume_24h >= 1_000_000 or liquidity >= 500_000:
            confidence = 'very_high'
        elif volume_24h >= 250_000 or liquidity >= 150_000:
            confidence = 'high'
        elif volume_24h >= 50_000 or liquidity >= 25_000:
            confidence = 'medium'
        else:
            confidence = 'low'

        if change_pts >= 8:
            status = 'breaking'
        elif change_pts >= 3:
            status = 'accelerating'
        elif change_pts <= -5:
            status = 'cooling'
        else:
            status = 'emerging'

        timeframe_min, timeframe_max = self._prediction_timeframe(meta.get('end_date'))

        # Build an odds summary for evidence.
        outcomes = meta.get('outcomes') or []
        prices = meta.get('outcome_prices') or []
        if outcomes and prices:
            odds_summary = ", ".join(
                f"{o} {round(float(p) * 100)}%" for o, p in zip(outcomes, prices)
            )
        else:
            odds_summary = f"{top_outcome} {prob_int}%"

        slug = meta.get('slug') or re.sub(r'[^a-z0-9]+', '-', question.lower()).strip('-')[:40]
        signal_id = f"pm-{slug}" if slug else f"pm-{row.get('id', 'market')}"

        change_word = "up" if change_pts > 0 else "down" if change_pts < 0 else "flat"
        related_tickers = [
            {
                'symbol': t,
                'name': t,
                'exposure': 'mixed',
                'relevanceScore': 85 - (i * 5),
            }
            for i, t in enumerate(tickers)
        ]

        why_it_matters = (
            "Prediction-market odds reflect real capital at risk and often shift "
            "before mainstream coverage does."
        )
        if tickers:
            why_it_matters += f" Watch {', '.join(tickers)} for read-through."

        created_at = row.get('created_at') or datetime.utcnow().isoformat()

        return {
            'id': signal_id,
            'title': question[:120],
            'summary': (
                f"Polymarket prices \"{top_outcome}\" at {prob_int}% "
                f"(${volume_24h:,.0f} traded in 24h, {change_word} {abs(change_pts)} pts)."
            ),
            'fullDescription': (
                meta.get('description')
                or f"Traders on Polymarket price this market at {prob_int}% for \"{top_outcome}\". "
                   f"Odds moved {change_word} {abs(change_pts)} points over the past 24 hours "
                   f"on ${volume_24h:,.0f} of volume."
            ),
            'whyItMatters': why_it_matters,
            'eventProbability': prob_int,
            'accelerationScore': accel,
            'confidence': confidence,
            'status': status,
            'timeframeMin': timeframe_min,
            'timeframeMax': timeframe_max,
            'timeframeUnit': 'days',
            'change24h': change_pts,
            'totalMentions': int(volume_24h),
            'relatedTickers': related_tickers,
            'sourceBreakdown': [{
                'platform': 'polymarket',
                'mentions': int(volume_24h),
                'percentChange24h': change_pts,
            }],
            'recentEvidence': [{
                'id': 'pm-0',
                'timestamp': created_at,
                'platform': 'polymarket',
                'title': question[:100],
                'snippet': odds_summary,
                'url': url,
                'engagement': int(volume_24h),
            }],
            'velocityData': self._prediction_velocity(prob, change_pts),
            'aiInsight': (
                f"The market currently implies a {prob_int}% chance of \"{top_outcome}\". "
                + (f"Related tickers to watch: {', '.join(tickers)}. " if tickers else "")
                + "Treat this as a real-money probability, not a guarantee."
            ),
            'marketType': 'prediction',
            'impliedProbability': prob_int,
            'marketVolume24h': int(volume_24h),
            'marketUrl': url,
            'createdAt': created_at,
            'updatedAt': datetime.utcnow().isoformat(),
        }

    def _map_question_to_tickers(self, text: str) -> list[str]:
        """Map prediction-market prose to tradable tickers (conservative)."""
        lowered = text.lower()
        found: list[str] = []

        for keyword, tickers in QUESTION_TICKER_MAP.items():
            if keyword in lowered:
                for t in tickers:
                    if t not in found:
                        found.append(t)

        # Explicit $TICKER mentions only (bare-word matching is too noisy here).
        for match in re.finditer(r'\$([A-Z]{1,5})\b', text.upper()):
            ticker = match.group(1)
            if ticker in TRACKED_TICKERS and ticker not in found:
                found.append(ticker)

        return found[:5]

    @staticmethod
    def _prediction_timeframe(end_date) -> tuple[int, int]:
        """Days until the market resolves, when known."""
        if end_date:
            try:
                end = datetime.fromisoformat(str(end_date).replace("Z", "+00:00")).replace(tzinfo=None)
                days = (end - datetime.utcnow()).days
                if days >= 1:
                    return days, days
            except (ValueError, AttributeError):
                pass
        return 30, 90

    @staticmethod
    def _prediction_velocity(prob: float, change_pts: float) -> list[dict]:
        """Synthesize a 15-point implied-odds series ending at the current price."""
        now = datetime.utcnow()
        start = max(0.0, min(100.0, prob - change_pts))
        data = []
        for days_ago in range(14, -1, -1):
            frac = (14 - days_ago) / 14
            value = start + (prob - start) * frac
            data.append({
                'timestamp': (now - timedelta(days=days_ago)).isoformat(),
                'value': round(max(0.0, min(100.0, value)), 1),
            })
        return data

    async def _generate_prediction_insight(self, signal: dict) -> str:
        """Use Claude for a sharp 2-sentence read on a prediction market."""
        if not self.client:
            return signal.get('aiInsight', '')

        tickers = [t['symbol'] for t in signal.get('relatedTickers', [])]
        prompt = f"""A Polymarket prediction market is priced as follows:

Question: {signal['title']}
Implied probability: {signal['eventProbability']}%
24h odds change: {signal['change24h']} points
24h volume: ${signal.get('marketVolume24h', 0):,}
{("Related tickers: " + ", ".join(tickers)) if tickers else ""}

Write a 2-sentence actionable insight for an investor: what this implied
probability and recent move suggest, and any read-through to the tickers. Be
concrete and avoid hype. Plain text only, no preamble."""

        try:
            response = await self.client.messages.create(
                model=BULK_MODEL,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            return text or signal.get('aiInsight', '')
        except Exception as e:
            print(f"Prediction insight generation failed: {e}")
            return signal.get('aiInsight', '')
