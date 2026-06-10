"use client";

import { cn } from "@/lib/utils";
import type { RelatedTicker } from "@/lib/types";
import { getExposureColor } from "@/lib/types";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface RelatedTickersProps {
  tickers: RelatedTicker[];
  layout?: "inline" | "list";
  maxShow?: number;
  className?: string;
}

const exposureIcons = {
  positive: TrendingUp,
  negative: TrendingDown,
  mixed: Minus,
};

export function RelatedTickers({ 
  tickers, 
  layout = "inline",
  maxShow = 4,
  className 
}: RelatedTickersProps) {
  const displayTickers = tickers.slice(0, maxShow);
  const remaining = tickers.length - maxShow;

  if (layout === "list") {
    return (
      <div className={cn("space-y-2", className)}>
        {displayTickers.map((ticker) => {
          const Icon = exposureIcons[ticker.exposure];
          return (
            <div 
              key={ticker.symbol}
              className="flex items-center justify-between py-2 px-3 bg-muted/30 rounded-lg"
            >
              <div className="flex items-center gap-3">
                <div className={cn(
                  "flex items-center justify-center w-8 h-8 rounded-md",
                  ticker.exposure === 'positive' ? "bg-ghost-green/10" :
                  ticker.exposure === 'negative' ? "bg-ghost-red/10" :
                  "bg-ghost-amber/10"
                )}>
                  <Icon className={cn("h-4 w-4", getExposureColor(ticker.exposure))} />
                </div>
                <div>
                  <div className="font-semibold">${ticker.symbol}</div>
                  <div className="text-xs text-muted-foreground">{ticker.name}</div>
                </div>
              </div>
              <div className="text-right">
                <div className={cn("text-sm font-medium", getExposureColor(ticker.exposure))}>
                  {ticker.exposure === 'positive' ? 'Positive' : 
                   ticker.exposure === 'negative' ? 'Negative' : 'Mixed'} Exposure
                </div>
                <div className="text-xs text-muted-foreground">
                  {ticker.relevanceScore}% relevance
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div className={cn("flex flex-wrap items-center gap-1.5", className)}>
      {displayTickers.map((ticker) => {
        const Icon = exposureIcons[ticker.exposure];
        return (
          <div 
            key={ticker.symbol}
            className={cn(
              "inline-flex items-center gap-1 px-2 py-1 rounded text-sm font-medium border",
              ticker.exposure === 'positive' ? "bg-ghost-green/10 border-ghost-green/20 text-ghost-green" :
              ticker.exposure === 'negative' ? "bg-ghost-red/10 border-ghost-red/20 text-ghost-red" :
              "bg-ghost-amber/10 border-ghost-amber/20 text-ghost-amber"
            )}
          >
            <Icon className="h-3 w-3" />
            <span>${ticker.symbol}</span>
          </div>
        );
      })}
      {remaining > 0 && (
        <span className="text-sm text-muted-foreground">
          +{remaining} more
        </span>
      )}
    </div>
  );
}
