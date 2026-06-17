"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { NavHeader } from "@/components/layout/nav-header";
import { 
  ProbabilityRing,
  AccelerationScore,
  VelocityChart,
  StatusBadge,
  ConfidenceBadge,
  SourceBreakdown,
  RelatedTickers,
  WatchlistButton,
  EvidenceTimeline,
  FinancialDisclaimer,
} from "@/components/ghost";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api-client";
import type { Signal } from "@/lib/types";
import { formatTimeframe } from "@/lib/types";
import { ArrowLeft, Clock, Brain, ArrowUp, ArrowDown, Share2, AlertCircle, Activity, ExternalLink } from "lucide-react";

interface SignalDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function SignalDetailPage({ params }: SignalDetailPageProps) {
  const resolvedParams = use(params);
  const router = useRouter();
  const [signal, setSignal] = useState<Signal | null>(null);
  const [loading, setLoading] = useState(true);
  const [usingMockData, setUsingMockData] = useState(false);

  useEffect(() => {
    async function loadSignal() {
      setLoading(true);
      try {
        const data = await apiClient.getSignal(resolvedParams.id);
        if (data) {
          setSignal(data);
          setUsingMockData(apiClient.isUsingMockData());
        } else {
          router.push('/signals');
        }
      } catch (error) {
        console.error('Failed to load signal:', error);
        router.push('/signals');
      } finally {
        setLoading(false);
      }
    }
    loadSignal();
  }, [resolvedParams.id, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <NavHeader />
        <main className="container mx-auto px-4 py-8">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-32" />
            <div className="h-12 bg-muted rounded w-2/3" />
            <div className="h-24 bg-muted rounded" />
          </div>
        </main>
      </div>
    );
  }

  if (!signal) {
    return null;
  }

  const isPositiveChange = signal.change24h > 0;
  const chartColor = isPositiveChange ? "green" : signal.change24h < 0 ? "red" : "neutral";
  const isPrediction = signal.marketType === "prediction";

  return (
    <div className="min-h-screen bg-background">
      <NavHeader />
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <Link href="/signals">
            <Button variant="ghost" size="sm" className="gap-2 -ml-2 text-muted-foreground">
              <ArrowLeft className="h-4 w-4" />
              Back to Signals
            </Button>
          </Link>
        </div>

        {usingMockData && (
          <div className="mb-6 p-4 rounded-lg border border-ghost-amber/20 bg-ghost-amber/5 flex items-center gap-3">
            <AlertCircle className="h-5 w-5 text-ghost-amber" />
            <p className="text-sm text-muted-foreground">
              Showing demo data. Start the backend for live signals.
            </p>
          </div>
        )}

        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <div>
              <div className="flex flex-wrap items-center gap-3 mb-4">
                <StatusBadge status={signal.status} />
                <ConfidenceBadge confidence={signal.confidence} />
                {isPrediction && (
                  <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-ghost-blue/10 text-ghost-blue border border-ghost-blue/20">
                    <Activity className="h-3 w-3" />
                    Prediction market
                  </span>
                )}
                <span className={`text-sm tabular-nums flex items-center gap-1 ${isPositiveChange ? "text-ghost-green" : signal.change24h < 0 ? "text-ghost-red" : "text-muted-foreground"}`}>
                  {isPositiveChange ? <ArrowUp className="h-3.5 w-3.5" /> : signal.change24h < 0 ? <ArrowDown className="h-3.5 w-3.5" /> : null}
                  {signal.change24h > 0 ? "+" : ""}{signal.change24h}% 24h
                </span>
              </div>
              
              <h1 className="text-3xl md:text-4xl font-bold mb-4">{signal.title}</h1>
              
              <p className="text-lg text-muted-foreground">
                {signal.fullDescription}
              </p>
            </div>

            <div className="p-6 rounded-xl border border-border bg-card">
              <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">
                Why This Matters
              </h2>
              <p className="text-foreground">{signal.whyItMatters}</p>
            </div>

            <div className="p-6 rounded-xl border border-border bg-card">
              <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
                Related Tickers
              </h2>
              <RelatedTickers tickers={signal.relatedTickers} layout="list" />
            </div>

            <div className="p-6 rounded-xl border border-border bg-card">
              <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
                Source Breakdown
              </h2>
              <SourceBreakdown sources={signal.sourceBreakdown} layout="vertical" />
            </div>

            <div className="p-6 rounded-xl border border-border bg-card">
              <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
                Recent Evidence
              </h2>
              <EvidenceTimeline evidence={signal.recentEvidence} />
            </div>

            <div className="p-6 rounded-xl border border-ghost-blue/20 bg-ghost-blue/5">
              <div className="flex items-start gap-3">
                <Brain className="h-5 w-5 text-ghost-blue shrink-0 mt-0.5" />
                <div>
                  <h2 className="font-semibold mb-2">AI Insight</h2>
                  <p className="text-muted-foreground">{signal.aiInsight}</p>
                </div>
              </div>
            </div>

            <FinancialDisclaimer variant="card" />
          </div>

          <div className="lg:col-span-1">
            <div className="sticky top-24 space-y-6">
              <div className="p-6 rounded-xl border border-border bg-card">
                <div className="text-center mb-6">
                  <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-4">
                    Event Probability
                  </h3>
                  <ProbabilityRing value={signal.eventProbability} size="lg" />
                </div>

                <div className="space-y-4 pt-4 border-t border-border">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-muted-foreground">Acceleration Score</span>
                      <AccelerationScore score={signal.accelerationScore} size="sm" showIcon={false} />
                    </div>
                    <VelocityChart data={signal.velocityData} height={48} color={chartColor} />
                    <p className="text-xs text-muted-foreground mt-1 text-center">
                      Signal velocity (14 days)
                    </p>
                  </div>

                  <div className="flex items-center justify-between py-3 border-t border-border">
                    <span className="text-sm text-muted-foreground">Estimated Timeframe</span>
                    <span className="text-sm font-medium flex items-center gap-1.5">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      {formatTimeframe(signal.timeframeMin, signal.timeframeMax, signal.timeframeUnit)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-3 border-t border-border">
                    <span className="text-sm text-muted-foreground">
                      {isPrediction ? "24h Volume" : "Total Mentions"}
                    </span>
                    <span className="text-sm font-medium tabular-nums">
                      {isPrediction
                        ? `$${(signal.marketVolume24h ?? signal.totalMentions).toLocaleString()}`
                        : signal.totalMentions.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex gap-2">
                <WatchlistButton 
                  type="signal" 
                  id={signal.id} 
                  showLabel 
                  variant="outline"
                  className="flex-1"
                />
                <Button variant="outline" size="icon">
                  <Share2 className="h-4 w-4" />
                </Button>
              </div>

              {isPrediction && signal.marketUrl && (
                <a
                  href={signal.marketUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 w-full px-4 py-2.5 rounded-lg border border-ghost-blue/20 bg-ghost-blue/5 text-sm font-medium text-ghost-blue hover:bg-ghost-blue/10 transition-colors"
                >
                  View on Polymarket
                  <ExternalLink className="h-4 w-4" />
                </a>
              )}

              <FinancialDisclaimer />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
