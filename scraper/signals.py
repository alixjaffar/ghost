"""
Signal Generation for Ghost

This module transforms raw scraped content and ticker mentions into
actionable signals with probability, acceleration, and confidence scores.
"""
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional
import anthropic

from config import ANTHROPIC_API_KEY, BULK_MODEL, INSIGHT_MODEL
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
