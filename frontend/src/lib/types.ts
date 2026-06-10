/**
 * Ghost Data Models
 * 
 * These types define the structure of signals, tickers, and related data.
 * In production, these would be populated from real data sources:
 * - Social media APIs (Reddit, Twitter/X, YouTube)
 * - News aggregation services
 * - Podcast transcript services
 * - Web scraping infrastructure
 * 
 * The scoring algorithms (acceleration, confidence, probability) would use:
 * - Mention velocity (rate of change in discussions)
 * - Cross-platform spread (diversity of sources)
 * - Source credibility weighting
 * - Historical pattern matching
 * - NLP sentiment analysis
 */

export type SignalStatus = 'emerging' | 'accelerating' | 'breaking' | 'cooling';

export type ConfidenceLevel = 'low' | 'medium' | 'high' | 'very_high';

export type SourcePlatform = 
  | 'reddit' 
  | 'twitter' 
  | 'youtube' 
  | 'tiktok' 
  | 'instagram' 
  | 'podcasts' 
  | 'news' 
  | 'comments';

export type TickerExposure = 'positive' | 'negative' | 'mixed';

export interface SourceBreakdown {
  platform: SourcePlatform;
  mentions: number;
  percentChange24h: number;
}

export interface RelatedTicker {
  symbol: string;
  name: string;
  exposure: TickerExposure;
  relevanceScore: number;
}

export interface EvidenceItem {
  id: string;
  timestamp: string;
  platform: SourcePlatform;
  title: string;
  snippet: string;
  url?: string;
  engagement?: number;
}

export interface VelocityDataPoint {
  timestamp: string;
  value: number;
}

export interface Signal {
  id: string;
  title: string;
  summary: string;
  fullDescription: string;
  whyItMatters: string;
  
  eventProbability: number;
  accelerationScore: number;
  confidence: ConfidenceLevel;
  status: SignalStatus;
  
  timeframeMin: number;
  timeframeMax: number;
  timeframeUnit: 'hours' | 'days' | 'weeks' | 'months';
  
  change24h: number;
  totalMentions: number;
  
  relatedTickers: RelatedTicker[];
  sourceBreakdown: SourceBreakdown[];
  recentEvidence: EvidenceItem[];
  velocityData: VelocityDataPoint[];
  
  aiInsight: string;
  
  createdAt: string;
  updatedAt: string;
}

export interface WatchlistItem {
  type: 'signal' | 'ticker';
  id: string;
  addedAt: string;
}

export interface Watchlist {
  items: WatchlistItem[];
}

export function getStatusColor(status: SignalStatus): string {
  switch (status) {
    case 'breaking': return 'text-ghost-red';
    case 'accelerating': return 'text-ghost-green';
    case 'emerging': return 'text-ghost-amber';
    case 'cooling': return 'text-muted-foreground';
  }
}

export function getStatusBgColor(status: SignalStatus): string {
  switch (status) {
    case 'breaking': return 'bg-ghost-red/10 border-ghost-red/20';
    case 'accelerating': return 'bg-ghost-green/10 border-ghost-green/20';
    case 'emerging': return 'bg-ghost-amber/10 border-ghost-amber/20';
    case 'cooling': return 'bg-muted/50 border-border';
  }
}

export function getConfidenceLabel(confidence: ConfidenceLevel): string {
  switch (confidence) {
    case 'very_high': return 'Very High';
    case 'high': return 'High';
    case 'medium': return 'Medium';
    case 'low': return 'Low';
  }
}

export function getExposureColor(exposure: TickerExposure): string {
  switch (exposure) {
    case 'positive': return 'text-ghost-green';
    case 'negative': return 'text-ghost-red';
    case 'mixed': return 'text-ghost-amber';
  }
}

export function getPlatformIcon(platform: SourcePlatform): string {
  switch (platform) {
    case 'reddit': return 'MessageSquare';
    case 'twitter': return 'AtSign';
    case 'youtube': return 'Video';
    case 'tiktok': return 'Music';
    case 'instagram': return 'Camera';
    case 'podcasts': return 'Mic';
    case 'news': return 'Newspaper';
    case 'comments': return 'MessageCircle';
  }
}

export function formatTimeframe(min: number, max: number, unit: string): string {
  if (min === max) {
    return `${min} ${unit}`;
  }
  return `${min}-${max} ${unit}`;
}
