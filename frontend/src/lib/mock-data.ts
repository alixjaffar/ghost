/**
 * Mock Data for Ghost MVP
 * 
 * This file contains realistic sample data for demonstrating the Ghost platform.
 * All signals, probabilities, and scores are illustrative examples only.
 * 
 * DISCLAIMER: These are demo estimates for product demonstration purposes.
 * They do not constitute financial advice or predictions about actual market events.
 * 
 * In production, this data would be replaced with:
 * - Real-time social media monitoring (Reddit API, Twitter API, YouTube Data API)
 * - News aggregation services (NewsAPI, Polygon.io news)
 * - Podcast transcript analysis (Spotify, Apple Podcasts APIs)
 * - NLP-based sentiment and entity extraction
 * - Proprietary scoring algorithms based on:
 *   - Mention velocity across platforms
 *   - Cross-platform spread patterns
 *   - Source credibility weighting
 *   - Historical correlation analysis
 */

import type { Signal, VelocityDataPoint } from './types';

function generateVelocityData(days: number, trend: 'up' | 'down' | 'stable', volatility: number = 0.2): VelocityDataPoint[] {
  const data: VelocityDataPoint[] = [];
  let baseValue = 30 + Math.random() * 20;
  
  for (let i = days; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    
    const trendFactor = trend === 'up' ? 1.03 : trend === 'down' ? 0.97 : 1;
    const noise = (Math.random() - 0.5) * volatility * baseValue;
    baseValue = Math.max(10, baseValue * trendFactor + noise);
    
    data.push({
      timestamp: date.toISOString(),
      value: Math.round(baseValue),
    });
  }
  
  return data;
}

export const mockSignals: Signal[] = [
  {
    id: 'ai-chip-supply',
    title: 'AI Chip Supply Constraint',
    summary: 'Discussion across Reddit, X, YouTube, and industry news is accelerating around GPU shortages, supplier delays, and data center capacity limitations.',
    fullDescription: 'Multiple signals indicate growing concern about AI chip supply constraints. Discussions about GPU availability, NVIDIA allocation policies, and data center build-out delays have increased significantly across social platforms and industry publications. Enterprise customers are reportedly facing 6-12 month lead times for high-end AI accelerators.',
    whyItMatters: 'Supply constraints could impact AI infrastructure buildout timelines, affect cloud provider capacity, and influence semiconductor company valuations. Companies with secured supply agreements may have competitive advantages.',
    eventProbability: 78,
    accelerationScore: 92,
    confidence: 'high',
    status: 'accelerating',
    timeframeMin: 30,
    timeframeMax: 60,
    timeframeUnit: 'days',
    change24h: 12.5,
    totalMentions: 24800,
    relatedTickers: [
      { symbol: 'NVDA', name: 'NVIDIA Corporation', exposure: 'mixed', relevanceScore: 98 },
      { symbol: 'AVGO', name: 'Broadcom Inc.', exposure: 'positive', relevanceScore: 85 },
      { symbol: 'TSM', name: 'Taiwan Semiconductor', exposure: 'positive', relevanceScore: 92 },
      { symbol: 'ASML', name: 'ASML Holding', exposure: 'positive', relevanceScore: 78 },
    ],
    sourceBreakdown: [
      { platform: 'reddit', mentions: 8500, percentChange24h: 15 },
      { platform: 'twitter', mentions: 10300, percentChange24h: 18 },
      { platform: 'youtube', mentions: 3200, percentChange24h: 8 },
      { platform: 'news', mentions: 2100, percentChange24h: 22 },
      { platform: 'podcasts', mentions: 700, percentChange24h: 5 },
    ],
    recentEvidence: [
      { id: 'e1', timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), platform: 'reddit', title: 'r/hardware: "NVIDIA H100 lead times now 8-10 months"', snippet: 'Multiple enterprise buyers reporting extended wait times...', engagement: 2400 },
      { id: 'e2', timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), platform: 'twitter', title: 'Industry analyst: "Data center capacity becoming bottleneck"', snippet: 'Power and cooling constraints adding to chip shortage...', engagement: 8900 },
      { id: 'e3', timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(), platform: 'news', title: 'Bloomberg: TSM raising prices on advanced nodes', snippet: 'Taiwan Semiconductor reportedly increasing prices 3-5%...', engagement: 15000 },
    ],
    velocityData: generateVelocityData(14, 'up', 0.15),
    aiInsight: 'Multiple signals point to tightening AI chip supply over the next 1-2 quarters. Monitor inventory levels and supplier updates. Companies with diversified supply chains may be better positioned.',
    createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'data-center-power',
    title: 'Data Center Power Demand Surge',
    summary: 'Accelerating discussion about data center electricity consumption, grid capacity concerns, and utility company preparations for AI-driven demand.',
    fullDescription: 'Social media and news outlets are increasingly focused on the power requirements of AI data centers. Discussions highlight that a single large AI training run can consume as much electricity as a small town. Utilities are reportedly scrambling to meet projected demand.',
    whyItMatters: 'Power constraints could become a limiting factor for AI expansion. Utility companies and power infrastructure providers may see increased demand. Data centers in power-constrained regions may face operational challenges.',
    eventProbability: 72,
    accelerationScore: 85,
    confidence: 'high',
    status: 'accelerating',
    timeframeMin: 60,
    timeframeMax: 120,
    timeframeUnit: 'days',
    change24h: 8.3,
    totalMentions: 18200,
    relatedTickers: [
      { symbol: 'VST', name: 'Vistra Corp', exposure: 'positive', relevanceScore: 88 },
      { symbol: 'CEG', name: 'Constellation Energy', exposure: 'positive', relevanceScore: 85 },
      { symbol: 'EQIX', name: 'Equinix', exposure: 'mixed', relevanceScore: 82 },
      { symbol: 'DLR', name: 'Digital Realty', exposure: 'mixed', relevanceScore: 78 },
    ],
    sourceBreakdown: [
      { platform: 'reddit', mentions: 5200, percentChange24h: 12 },
      { platform: 'twitter', mentions: 7800, percentChange24h: 9 },
      { platform: 'youtube', mentions: 2100, percentChange24h: 15 },
      { platform: 'news', mentions: 2800, percentChange24h: 6 },
      { platform: 'podcasts', mentions: 300, percentChange24h: 3 },
    ],
    recentEvidence: [
      { id: 'e1', timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(), platform: 'news', title: 'WSJ: Tech giants racing to secure power agreements', snippet: 'Microsoft, Google, Amazon competing for utility contracts...', engagement: 12000 },
      { id: 'e2', timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), platform: 'reddit', title: 'r/technology: "AI data centers using 1% of US electricity"', snippet: 'IEA report shows dramatic increase in data center power use...', engagement: 3200 },
    ],
    velocityData: generateVelocityData(14, 'up', 0.12),
    aiInsight: 'Power infrastructure is becoming a key consideration for AI expansion. Watch for utility earnings calls mentioning data center contracts and grid capacity investments.',
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'glp1-adoption',
    title: 'GLP-1 Drug Adoption Accelerating',
    summary: 'Consumer interest and discussion around weight loss medications like Ozempic and Mounjaro continues to surge across social platforms.',
    fullDescription: 'Social media discussions about GLP-1 receptor agonists have reached unprecedented levels. Topics include accessibility, insurance coverage, compounding pharmacies, and potential health system impacts. Celebrity endorsements and user testimonials are driving viral spread.',
    whyItMatters: 'Rapid adoption could drive significant revenue growth for pharmaceutical companies. Secondary effects may impact food & beverage, fitness, and healthcare sectors as consumer behavior shifts.',
    eventProbability: 85,
    accelerationScore: 88,
    confidence: 'very_high',
    status: 'accelerating',
    timeframeMin: 30,
    timeframeMax: 90,
    timeframeUnit: 'days',
    change24h: 5.2,
    totalMentions: 42500,
    relatedTickers: [
      { symbol: 'LLY', name: 'Eli Lilly', exposure: 'positive', relevanceScore: 95 },
      { symbol: 'NVO', name: 'Novo Nordisk', exposure: 'positive', relevanceScore: 95 },
      { symbol: 'HIMS', name: 'Hims & Hers Health', exposure: 'positive', relevanceScore: 72 },
      { symbol: 'WW', name: 'WW International', exposure: 'negative', relevanceScore: 68 },
    ],
    sourceBreakdown: [
      { platform: 'tiktok', mentions: 15800, percentChange24h: 8 },
      { platform: 'reddit', mentions: 12300, percentChange24h: 4 },
      { platform: 'twitter', mentions: 8900, percentChange24h: 6 },
      { platform: 'youtube', mentions: 3800, percentChange24h: 12 },
      { platform: 'instagram', mentions: 1700, percentChange24h: 3 },
    ],
    recentEvidence: [
      { id: 'e1', timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), platform: 'tiktok', title: 'Viral: "My 6-month Ozempic journey" (2.1M views)', snippet: 'User documents 45lb weight loss, sparking discussion...', engagement: 2100000 },
      { id: 'e2', timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(), platform: 'news', title: 'FDA: Tirzepatide approved for weight maintenance', snippet: 'Expanded indication could broaden patient pool...', engagement: 8500 },
    ],
    velocityData: generateVelocityData(14, 'up', 0.08),
    aiInsight: 'GLP-1 adoption shows no signs of slowing. Watch for supply chain updates from LLY and NVO, and monitor secondary effects on consumer discretionary sectors.',
    createdAt: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'nuclear-renaissance',
    title: 'Nuclear Energy Renaissance',
    summary: 'Growing public and institutional interest in nuclear power as a clean energy solution, driven by AI power demands and climate goals.',
    fullDescription: 'Discussion about nuclear energy has shifted from skepticism to enthusiasm across social platforms. Topics include small modular reactors (SMRs), data center power partnerships, and nuclear plant restarts. Tech companies announcing nuclear power agreements are driving narrative acceleration.',
    whyItMatters: 'A nuclear renaissance could reshape energy markets, benefit uranium miners and reactor builders, and provide a solution to data center power constraints.',
    eventProbability: 65,
    accelerationScore: 78,
    confidence: 'medium',
    status: 'emerging',
    timeframeMin: 6,
    timeframeMax: 18,
    timeframeUnit: 'months',
    change24h: 15.8,
    totalMentions: 12400,
    relatedTickers: [
      { symbol: 'CCJ', name: 'Cameco Corporation', exposure: 'positive', relevanceScore: 92 },
      { symbol: 'SMR', name: 'NuScale Power', exposure: 'positive', relevanceScore: 88 },
      { symbol: 'CEG', name: 'Constellation Energy', exposure: 'positive', relevanceScore: 85 },
      { symbol: 'URA', name: 'Global X Uranium ETF', exposure: 'positive', relevanceScore: 80 },
    ],
    sourceBreakdown: [
      { platform: 'reddit', mentions: 4200, percentChange24h: 22 },
      { platform: 'twitter', mentions: 5100, percentChange24h: 18 },
      { platform: 'youtube', mentions: 1800, percentChange24h: 25 },
      { platform: 'news', mentions: 1100, percentChange24h: 12 },
      { platform: 'podcasts', mentions: 200, percentChange24h: 8 },
    ],
    recentEvidence: [
      { id: 'e1', timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), platform: 'news', title: 'Microsoft signs nuclear power deal for AI data centers', snippet: 'Agreement to restart Three Mile Island reactor...', engagement: 45000 },
      { id: 'e2', timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(), platform: 'reddit', title: 'r/energy: "Nuclear sentiment has completely flipped"', snippet: 'Discussion thread analyzing changing public perception...', engagement: 1800 },
    ],
    velocityData: generateVelocityData(14, 'up', 0.2),
    aiInsight: 'Nuclear energy narrative is accelerating faster than infrastructure can respond. Long-term play with near-term volatility expected. Monitor regulatory developments and tech company announcements.',
    createdAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'shipping-disruption',
    title: 'Red Sea Shipping Disruption',
    summary: 'Continued attacks on commercial vessels in the Red Sea are forcing shipping reroutes, increasing costs and delivery times.',
    fullDescription: 'Geopolitical tensions continue to disrupt one of the world\'s busiest shipping lanes. Major carriers are avoiding the Suez Canal, adding 10-14 days to Europe-Asia routes. Discussion focuses on supply chain impacts, shipping rate increases, and inflation implications.',
    whyItMatters: 'Extended disruptions could reignite supply chain issues, increase transportation costs, and potentially impact inflation. Shipping companies may benefit from higher rates while retailers face margin pressure.',
    eventProbability: 70,
    accelerationScore: 62,
    confidence: 'high',
    status: 'emerging',
    timeframeMin: 30,
    timeframeMax: 90,
    timeframeUnit: 'days',
    change24h: -3.2,
    totalMentions: 8900,
    relatedTickers: [
      { symbol: 'ZIM', name: 'ZIM Integrated Shipping', exposure: 'positive', relevanceScore: 90 },
      { symbol: 'SBLK', name: 'Star Bulk Carriers', exposure: 'positive', relevanceScore: 82 },
      { symbol: 'TGT', name: 'Target Corporation', exposure: 'negative', relevanceScore: 65 },
      { symbol: 'WMT', name: 'Walmart Inc.', exposure: 'negative', relevanceScore: 62 },
    ],
    sourceBreakdown: [
      { platform: 'twitter', mentions: 3800, percentChange24h: -5 },
      { platform: 'news', mentions: 2900, percentChange24h: -2 },
      { platform: 'reddit', mentions: 1500, percentChange24h: -8 },
      { platform: 'youtube', mentions: 500, percentChange24h: 2 },
      { platform: 'podcasts', mentions: 200, percentChange24h: 0 },
    ],
    recentEvidence: [
      { id: 'e1', timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(), platform: 'news', title: 'Maersk extends Red Sea avoidance through Q2', snippet: 'Major carrier continues Cape of Good Hope routing...', engagement: 5600 },
      { id: 'e2', timestamp: new Date(Date.now() - 18 * 60 * 60 * 1000).toISOString(), platform: 'twitter', title: 'Shipping rates Asia-Europe up 250% YoY', snippet: 'Freightos index shows continued rate elevation...', engagement: 2100 },
    ],
    velocityData: generateVelocityData(14, 'stable', 0.15),
    aiInsight: 'Shipping disruption narrative has stabilized but remains elevated. Market may be pricing in extended disruption. Watch for any de-escalation signals or further escalation.',
    createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'humanoid-robots',
    title: 'Humanoid Robotics Breakthrough',
    summary: 'Viral videos of Tesla Optimus and Figure robots performing complex tasks are driving unprecedented retail interest in humanoid robotics.',
    fullDescription: 'Consumer fascination with humanoid robots has exploded following viral demonstrations. Discussion focuses on timeline to commercial viability, labor market implications, and investment opportunities. Tesla\'s Optimus program and well-funded startups like Figure are central to the narrative.',
    whyItMatters: 'If humanoid robots achieve commercial viability, implications span manufacturing, logistics, healthcare, and consumer markets. Early movers in hardware and AI could see significant value creation.',
    eventProbability: 45,
    accelerationScore: 82,
    confidence: 'medium',
    status: 'accelerating',
    timeframeMin: 12,
    timeframeMax: 36,
    timeframeUnit: 'months',
    change24h: 28.5,
    totalMentions: 15600,
    relatedTickers: [
      { symbol: 'TSLA', name: 'Tesla Inc.', exposure: 'positive', relevanceScore: 95 },
      { symbol: 'NVDA', name: 'NVIDIA Corporation', exposure: 'positive', relevanceScore: 78 },
      { symbol: 'ISRG', name: 'Intuitive Surgical', exposure: 'positive', relevanceScore: 65 },
      { symbol: 'ROK', name: 'Rockwell Automation', exposure: 'positive', relevanceScore: 60 },
    ],
    sourceBreakdown: [
      { platform: 'youtube', mentions: 5800, percentChange24h: 35 },
      { platform: 'twitter', mentions: 4900, percentChange24h: 32 },
      { platform: 'reddit', mentions: 3200, percentChange24h: 25 },
      { platform: 'tiktok', mentions: 1200, percentChange24h: 42 },
      { platform: 'news', mentions: 500, percentChange24h: 15 },
    ],
    recentEvidence: [
      { id: 'e1', timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), platform: 'youtube', title: 'Tesla Optimus folds laundry autonomously (15M views)', snippet: 'Viral video shows robot performing household task...', engagement: 15000000 },
      { id: 'e2', timestamp: new Date(Date.now() - 10 * 60 * 60 * 1000).toISOString(), platform: 'twitter', title: 'Figure raises $675M at $2.6B valuation', snippet: 'Humanoid robotics startup attracts major investors...', engagement: 28000 },
    ],
    velocityData: generateVelocityData(14, 'up', 0.25),
    aiInsight: 'Humanoid robotics narrative is highly speculative but accelerating rapidly. High volatility expected. Focus on companies with demonstrated capabilities rather than pure hype.',
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'china-deflation',
    title: 'China Deflation Concerns',
    summary: 'Growing discussion about deflationary pressures in China and potential spillover effects on global markets and commodities.',
    fullDescription: 'Economic data from China showing falling prices is generating concern across financial media and social platforms. Discussion centers on consumer confidence, property market weakness, and implications for global trade. Some compare the situation to Japan\'s "lost decade."',
    whyItMatters: 'Chinese deflation could impact global commodity demand, multinational earnings, and emerging market sentiment. May also influence Fed policy expectations if deflationary pressure spreads.',
    eventProbability: 58,
    accelerationScore: 55,
    confidence: 'medium',
    status: 'emerging',
    timeframeMin: 60,
    timeframeMax: 180,
    timeframeUnit: 'days',
    change24h: 2.1,
    totalMentions: 9200,
    relatedTickers: [
      { symbol: 'FXI', name: 'iShares China Large-Cap ETF', exposure: 'negative', relevanceScore: 88 },
      { symbol: 'BABA', name: 'Alibaba Group', exposure: 'negative', relevanceScore: 82 },
      { symbol: 'CAT', name: 'Caterpillar Inc.', exposure: 'negative', relevanceScore: 70 },
      { symbol: 'FCX', name: 'Freeport-McMoRan', exposure: 'negative', relevanceScore: 75 },
    ],
    sourceBreakdown: [
      { platform: 'twitter', mentions: 4100, percentChange24h: 3 },
      { platform: 'news', mentions: 2800, percentChange24h: 5 },
      { platform: 'reddit', mentions: 1500, percentChange24h: -2 },
      { platform: 'youtube', mentions: 600, percentChange24h: 8 },
      { platform: 'podcasts', mentions: 200, percentChange24h: 0 },
    ],
    recentEvidence: [
      { id: 'e1', timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(), platform: 'news', title: 'China CPI falls for fifth consecutive month', snippet: 'Consumer prices decline 0.3% year-over-year...', engagement: 8200 },
      { id: 'e2', timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), platform: 'twitter', title: 'Economist: "China facing demand crisis"', snippet: 'Analysis of structural challenges in Chinese economy...', engagement: 4500 },
    ],
    velocityData: generateVelocityData(14, 'stable', 0.1),
    aiInsight: 'China deflation narrative is persistent but not accelerating. Monitor for stimulus announcements or further deterioration in economic data.',
    createdAt: new Date(Date.now() - 21 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'copper-squeeze',
    title: 'Copper Supply Squeeze',
    summary: 'Mining disruptions and surging electrification demand are creating discussion about a potential copper supply deficit.',
    fullDescription: 'Multiple mining disruptions combined with accelerating demand from EVs, data centers, and grid infrastructure are fueling concerns about copper supply. Discussion highlights that no major new mines are expected online for years while demand projections continue rising.',
    whyItMatters: 'Copper is essential for electrification. A sustained supply deficit could increase costs across clean energy, automotive, and construction sectors while benefiting mining companies.',
    eventProbability: 62,
    accelerationScore: 68,
    confidence: 'medium',
    status: 'emerging',
    timeframeMin: 90,
    timeframeMax: 180,
    timeframeUnit: 'days',
    change24h: 6.8,
    totalMentions: 7800,
    relatedTickers: [
      { symbol: 'FCX', name: 'Freeport-McMoRan', exposure: 'positive', relevanceScore: 95 },
      { symbol: 'SCCO', name: 'Southern Copper', exposure: 'positive', relevanceScore: 90 },
      { symbol: 'COPX', name: 'Global X Copper Miners ETF', exposure: 'positive', relevanceScore: 85 },
      { symbol: 'RIO', name: 'Rio Tinto', exposure: 'positive', relevanceScore: 72 },
    ],
    sourceBreakdown: [
      { platform: 'twitter', mentions: 3200, percentChange24h: 8 },
      { platform: 'reddit', mentions: 2400, percentChange24h: 12 },
      { platform: 'news', mentions: 1500, percentChange24h: 5 },
      { platform: 'youtube', mentions: 500, percentChange24h: 15 },
      { platform: 'podcasts', mentions: 200, percentChange24h: 3 },
    ],
    recentEvidence: [
      { id: 'e1', timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(), platform: 'news', title: 'Anglo American cuts copper production guidance', snippet: 'Major miner reduces output forecast by 8%...', engagement: 3800 },
      { id: 'e2', timestamp: new Date(Date.now() - 16 * 60 * 60 * 1000).toISOString(), platform: 'reddit', title: 'r/commodities: "Copper is the new oil"', snippet: 'Discussion thread on electrification demand projections...', engagement: 1200 },
    ],
    velocityData: generateVelocityData(14, 'up', 0.12),
    aiInsight: 'Copper supply narrative aligns with long-term electrification trends. Near-term price moves may be volatile, but structural thesis remains intact.',
    createdAt: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

export function getSignalById(id: string): Signal | undefined {
  return mockSignals.find(signal => signal.id === id);
}

export function searchSignals(query: string): Signal[] {
  const lowerQuery = query.toLowerCase();
  return mockSignals.filter(signal => 
    signal.title.toLowerCase().includes(lowerQuery) ||
    signal.summary.toLowerCase().includes(lowerQuery) ||
    signal.relatedTickers.some(t => 
      t.symbol.toLowerCase().includes(lowerQuery) ||
      t.name.toLowerCase().includes(lowerQuery)
    )
  );
}

export function getSignalsByStatus(status: Signal['status']): Signal[] {
  return mockSignals.filter(signal => signal.status === status);
}

export function getTopSignals(limit: number = 5): Signal[] {
  return [...mockSignals]
    .sort((a, b) => b.accelerationScore - a.accelerationScore)
    .slice(0, limit);
}
