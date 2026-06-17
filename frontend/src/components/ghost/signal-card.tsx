"use client";

import Link from "next/link";
import { cn } from "@/lib/utils";
import type { Signal } from "@/lib/types";
import { formatTimeframe } from "@/lib/types";
import { ProbabilityRing } from "./probability-ring";
import { AccelerationScore } from "./acceleration-score";
import { StatusBadge } from "./status-badge";
import { ConfidenceBadge } from "./confidence-badge";
import { VelocityChart } from "./velocity-chart";
import { RelatedTickers } from "./related-tickers";
import { SourceBreakdown } from "./source-breakdown";
import { WatchlistButton } from "./watchlist-button";
import { Clock, ArrowUp, ArrowDown, Activity } from "lucide-react";

interface SignalCardProps {
  signal: Signal;
  variant?: "default" | "compact";
  className?: string;
}

const PredictionBadge = () => (
  <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-ghost-blue/10 text-ghost-blue border border-ghost-blue/20">
    <Activity className="h-3 w-3" />
    Prediction market
  </span>
);

export function SignalCard({ signal, variant = "default", className }: SignalCardProps) {
  const isPositiveChange = signal.change24h > 0;
  const chartColor = isPositiveChange ? "green" : signal.change24h < 0 ? "red" : "neutral";
  const isPrediction = signal.marketType === "prediction";

  if (variant === "compact") {
    return (
      <Link 
        href={`/signals/${signal.id}`}
        className={cn(
          "block p-4 rounded-lg border border-border bg-card hover:bg-accent/50 transition-colors",
          className
        )}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <StatusBadge status={signal.status} size="sm" />
              {isPrediction && (
                <span className="inline-flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-ghost-blue/10 text-ghost-blue border border-ghost-blue/20">
                  <Activity className="h-2.5 w-2.5" />
                  Odds
                </span>
              )}
              <span className={cn(
                "text-xs tabular-nums flex items-center gap-0.5",
                isPositiveChange ? "text-ghost-green" : "text-ghost-red"
              )}>
                {isPositiveChange ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                {Math.abs(signal.change24h)}%
              </span>
            </div>
            <h3 className="font-semibold truncate">{signal.title}</h3>
            <p className="text-sm text-muted-foreground line-clamp-1 mt-1">
              {signal.summary}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <ProbabilityRing value={signal.eventProbability} size="sm" />
            <WatchlistButton type="signal" id={signal.id} size="sm" />
          </div>
        </div>
      </Link>
    );
  }

  return (
    <Link 
      href={`/signals/${signal.id}`}
      className={cn(
        "block p-5 rounded-xl border border-border bg-card hover:border-border/80 hover:bg-card/80 transition-all group",
        className
      )}
    >
      <div className="flex items-start justify-between gap-6">
        <div className="flex-1 min-w-0 space-y-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <StatusBadge status={signal.status} />
              <ConfidenceBadge confidence={signal.confidence} size="sm" />
              {isPrediction && <PredictionBadge />}
              <span className={cn(
                "text-sm tabular-nums flex items-center gap-1 ml-auto",
                isPositiveChange ? "text-ghost-green" : signal.change24h < 0 ? "text-ghost-red" : "text-muted-foreground"
              )}>
                {isPositiveChange ? <ArrowUp className="h-3.5 w-3.5" /> : signal.change24h < 0 ? <ArrowDown className="h-3.5 w-3.5" /> : null}
                {signal.change24h > 0 ? "+" : ""}{signal.change24h}% 24h
              </span>
            </div>
            <h3 className="text-xl font-semibold group-hover:text-primary transition-colors">
              {signal.title}
            </h3>
            <p className="text-muted-foreground mt-2 line-clamp-2">
              {signal.summary}
            </p>
          </div>

          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Clock className="h-4 w-4" />
              <span>
                {formatTimeframe(signal.timeframeMin, signal.timeframeMax, signal.timeframeUnit)}
              </span>
            </div>
            <div className="text-muted-foreground">
              {isPrediction
                ? `$${(signal.marketVolume24h ?? signal.totalMentions).toLocaleString()} 24h volume`
                : `${signal.totalMentions.toLocaleString()} mentions`}
            </div>
          </div>

          <RelatedTickers tickers={signal.relatedTickers} maxShow={4} />

          <SourceBreakdown sources={signal.sourceBreakdown} showChange={false} />
        </div>

        <div className="flex flex-col items-center gap-4 shrink-0">
          <ProbabilityRing value={signal.eventProbability} size="lg" />
          <AccelerationScore score={signal.accelerationScore} size="sm" />
          <div className="w-24">
            <VelocityChart 
              data={signal.velocityData} 
              height={32} 
              color={chartColor}
            />
          </div>
          <WatchlistButton type="signal" id={signal.id} />
        </div>
      </div>
    </Link>
  );
}
