"use client";

import { cn } from "@/lib/utils";
import type { EvidenceItem } from "@/lib/types";
import { formatDistanceToNow } from "date-fns";
import { 
  MessageSquare, 
  AtSign, 
  Video, 
  Music, 
  Camera, 
  Mic, 
  Newspaper,
  MessageCircle,
  ExternalLink,
  TrendingUp,
  BarChart3,
  Globe,
} from "lucide-react";

interface EvidenceTimelineProps {
  evidence: EvidenceItem[];
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
};

function formatEngagement(count: number): string {
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
  if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
  return count.toString();
}

export function EvidenceTimeline({ evidence, className }: EvidenceTimelineProps) {
  return (
    <div className={cn("space-y-4", className)}>
      {evidence.map((item, index) => {
        const Icon = platformIcons[item.platform] || Globe;
        let timeAgo = "recently";
        try {
          timeAgo = formatDistanceToNow(new Date(item.timestamp), { addSuffix: true });
        } catch {
          // Use default
        }
        
        return (
          <div key={item.id} className="relative pl-6">
            {index < evidence.length - 1 && (
              <div className="absolute left-[9px] top-6 bottom-0 w-px bg-border" />
            )}
            <div className="absolute left-0 top-1 w-[18px] h-[18px] rounded-full bg-muted flex items-center justify-center">
              <Icon className="h-3 w-3 text-muted-foreground" />
            </div>
            
            <div className="bg-muted/30 rounded-lg p-3 hover:bg-muted/50 transition-colors">
              <div className="flex items-start justify-between gap-2 mb-1">
                <span className="text-xs text-muted-foreground capitalize">
                  {item.platform} • {timeAgo}
                </span>
                {item.engagement !== undefined && item.engagement > 0 && (
                  <span className="text-xs text-muted-foreground tabular-nums">
                    {formatEngagement(item.engagement)} engagement
                  </span>
                )}
              </div>
              <h4 className="text-sm font-medium mb-1">{item.title}</h4>
              <p className="text-sm text-muted-foreground">{item.snippet}</p>
              {item.url && (
                <a 
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-primary hover:underline mt-2"
                  onClick={(e) => e.stopPropagation()}
                >
                  View source
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
