"use client";

import { cn } from "@/lib/utils";
import type { SourceBreakdown as SourceBreakdownType } from "@/lib/types";
import { 
  MessageSquare, 
  AtSign, 
  Video, 
  Music, 
  Camera, 
  Mic, 
  Newspaper,
  MessageCircle,
  TrendingUp,
  BarChart3,
  Globe,
} from "lucide-react";

interface SourceBreakdownProps {
  sources: SourceBreakdownType[];
  layout?: "horizontal" | "vertical";
  showChange?: boolean;
  className?: string;
}

const platformIcons: Record<string, React.ElementType> = {
  reddit: MessageSquare,
  twitter: AtSign,
  youtube: Video,
  tiktok: Music,
  instagram: Camera,
  podcasts: Mic,
  news: Newspaper,
  comments: MessageCircle,
  stocktwits: TrendingUp,
  polygon: BarChart3,
  polymarket: TrendingUp,
};

const platformLabels: Record<string, string> = {
  reddit: "Reddit",
  twitter: "X / Twitter",
  youtube: "YouTube",
  tiktok: "TikTok",
  instagram: "Instagram",
  podcasts: "Podcasts",
  news: "News",
  comments: "Comments",
  stocktwits: "StockTwits",
  polygon: "Polygon",
  polymarket: "Polymarket",
};

function formatMentions(count: number): string {
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
  if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
  return count.toString();
}

export function SourceBreakdown({ 
  sources, 
  layout = "horizontal",
  showChange = true,
  className 
}: SourceBreakdownProps) {
  const totalMentions = sources.reduce((sum, s) => sum + s.mentions, 0);
  const sortedSources = [...sources].sort((a, b) => b.mentions - a.mentions);

  if (layout === "vertical") {
    return (
      <div className={cn("space-y-3", className)}>
        {sortedSources.map((source) => {
          const Icon = platformIcons[source.platform] || Globe;
          const label = platformLabels[source.platform] || source.platform;
          const percent = totalMentions > 0 ? (source.mentions / totalMentions) * 100 : 0;
          
          return (
            <div key={source.platform} className="space-y-1.5">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4 text-muted-foreground" />
                  <span>{label}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="tabular-nums">{formatMentions(source.mentions)}</span>
                  {showChange && source.percentChange24h !== 0 && (
                    <span className={cn(
                      "text-xs tabular-nums",
                      source.percentChange24h > 0 ? "text-ghost-green" : "text-ghost-red"
                    )}>
                      {source.percentChange24h > 0 ? "+" : ""}{source.percentChange24h}%
                    </span>
                  )}
                </div>
              </div>
              <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-foreground/30 rounded-full transition-all"
                  style={{ width: `${percent}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div className={cn("flex flex-wrap gap-3", className)}>
      {sortedSources.slice(0, 5).map((source) => {
        const Icon = platformIcons[source.platform] || Globe;
        
        return (
          <div 
            key={source.platform} 
            className="flex items-center gap-1.5 text-sm text-muted-foreground"
          >
            <Icon className="h-3.5 w-3.5" />
            <span className="tabular-nums">{formatMentions(source.mentions)}</span>
            {showChange && source.percentChange24h !== 0 && (
              <span className={cn(
                "text-xs tabular-nums",
                source.percentChange24h > 0 ? "text-ghost-green" : "text-ghost-red"
              )}>
                {source.percentChange24h > 0 ? "+" : ""}{source.percentChange24h}%
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
