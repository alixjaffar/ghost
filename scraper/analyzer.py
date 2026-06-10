"""
Ghost Content Analyzer

Uses Claude to extract tickers and sentiment from content.
"""
import re
import json
from typing import Optional
import anthropic

from config import ANTHROPIC_API_KEY, BULK_MODEL, TRACKED_TICKERS
from sources.base import ContentItem


class ContentAnalyzer:
    """Analyzes content for tickers and sentiment using Claude."""
    
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
        self.tracked_tickers = set(TRACKED_TICKERS)
    
    async def analyze(self, content: ContentItem) -> list[dict]:
        """Analyze content and extract ticker mentions with sentiment."""
        # First try quick regex extraction
        regex_tickers = self._extract_tickers_regex(content.content)
        
        # If we found tickers and have no API, return basic mentions
        if not self.client:
            return [
                {
                    "ticker": ticker,
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "context": content.content[:200],
                }
                for ticker in regex_tickers
            ]
        
        # Use AI for better analysis
        try:
            return await self._analyze_with_ai(content, regex_tickers)
        except Exception as e:
            print(f"AI analysis failed: {e}")
            # Fall back to regex results
            return [
                {
                    "ticker": ticker,
                    "sentiment": "neutral",
                    "confidence": 0.3,
                    "context": content.content[:200],
                }
                for ticker in regex_tickers
            ]
    
    def _extract_tickers_regex(self, text: str) -> list[str]:
        """Extract tickers using regex patterns."""
        found = set()
        
        # Pattern 1: $TICKER format
        dollar_pattern = r'\$([A-Z]{1,5})\b'
        for match in re.finditer(dollar_pattern, text.upper()):
            ticker = match.group(1)
            if ticker in self.tracked_tickers:
                found.add(ticker)
        
        # Pattern 2: Common ticker mentions without $
        # Only match if it's a known ticker to avoid false positives
        for ticker in self.tracked_tickers:
            # Match ticker as whole word
            pattern = rf'\b{ticker}\b'
            if re.search(pattern, text.upper()):
                found.add(ticker)
        
        return list(found)
    
    async def _analyze_with_ai(self, content: ContentItem, hint_tickers: list[str]) -> list[dict]:
        """Use Claude to analyze content for tickers and sentiment."""
        # Truncate content to avoid token limits
        truncated_content = content.content[:2000]
        
        prompt = f"""Analyze this financial content and extract stock ticker mentions with sentiment.

Content:
{truncated_content}

{"Hint - these tickers might be mentioned: " + ", ".join(hint_tickers) if hint_tickers else ""}

For each ticker mentioned, determine:
1. The ticker symbol
2. Sentiment: bullish, bearish, or neutral
3. Confidence: 0.0 to 1.0
4. A brief context quote (max 100 chars)

Respond with JSON only:
{{"mentions": [
  {{"ticker": "NVDA", "sentiment": "bullish", "confidence": 0.8, "context": "expects strong AI demand..."}},
  ...
]}}

If no tickers are mentioned, return: {{"mentions": []}}"""

        try:
            response = await self.client.messages.create(
                model=BULK_MODEL,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            text = response.content[0].text
            
            # Extract JSON from response
            if '{' in text:
                json_str = text[text.find('{'):text.rfind('}')+1]
                data = json.loads(json_str)
                
                mentions = []
                for m in data.get("mentions", []):
                    ticker = m.get("ticker", "").upper()
                    # Validate ticker is in our tracked list
                    if ticker in self.tracked_tickers:
                        mentions.append({
                            "ticker": ticker,
                            "sentiment": m.get("sentiment", "neutral"),
                            "confidence": float(m.get("confidence", 0.5)),
                            "context": m.get("context", "")[:200],
                        })
                
                return mentions
            
            return []
            
        except json.JSONDecodeError:
            print("Failed to parse AI response as JSON")
            return []
        except Exception as e:
            print(f"AI analysis error: {e}")
            raise
