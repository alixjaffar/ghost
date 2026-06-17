"use client";

import { useState, useMemo, useEffect } from "react";
import { NavHeader } from "@/components/layout/nav-header";
import { SignalCard, FinancialDisclaimer } from "@/components/ghost";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api-client";
import type { Signal, SignalStatus } from "@/lib/types";
import { Zap, TrendingUp, Sparkles, TrendingDown, LayoutGrid, List, RefreshCw, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

const statusFilters: { value: SignalStatus | 'all'; label: string; icon: React.ElementType }[] = [
  { value: 'all', label: 'All Signals', icon: LayoutGrid },
  { value: 'breaking', label: 'Breaking', icon: Zap },
  { value: 'accelerating', label: 'Accelerating', icon: TrendingUp },
  { value: 'emerging', label: 'Emerging', icon: Sparkles },
  { value: 'cooling', label: 'Cooling', icon: TrendingDown },
];

const sortOptions = [
  { value: 'acceleration', label: 'Acceleration' },
  { value: 'probability', label: 'Probability' },
  { value: 'change', label: '24h Change' },
  { value: 'mentions', label: 'Mentions' },
];

export default function SignalsPage() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<SignalStatus | 'all'>('all');
  const [laneFilter, setLaneFilter] = useState<'all' | 'narrative' | 'prediction'>('all');
  const [sortBy, setSortBy] = useState<string>('acceleration');
  const [viewMode, setViewMode] = useState<'default' | 'compact'>('default');
  const [usingMockData, setUsingMockData] = useState(false);

  useEffect(() => {
    loadSignals();
  }, []);

  async function loadSignals() {
    setLoading(true);
    try {
      const data = await apiClient.getSignals();
      setSignals(data);
      setUsingMockData(apiClient.isUsingMockData());
    } catch (error) {
      console.error('Failed to load signals:', error);
    } finally {
      setLoading(false);
    }
  }

  const filteredAndSortedSignals = useMemo(() => {
    let filtered = [...signals];

    if (statusFilter !== 'all') {
      filtered = filtered.filter(s => s.status === statusFilter);
    }

    if (laneFilter === 'prediction') {
      filtered = filtered.filter(s => s.marketType === 'prediction');
    } else if (laneFilter === 'narrative') {
      filtered = filtered.filter(s => s.marketType !== 'prediction');
    }

    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'probability':
          return b.eventProbability - a.eventProbability;
        case 'change':
          return b.change24h - a.change24h;
        case 'mentions':
          return b.totalMentions - a.totalMentions;
        case 'acceleration':
        default:
          return b.accelerationScore - a.accelerationScore;
      }
    });
    
    return filtered;
  }, [signals, statusFilter, laneFilter, sortBy]);

  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = { all: signals.length };
    signals.forEach(s => {
      counts[s.status] = (counts[s.status] || 0) + 1;
    });
    return counts;
  }, [signals]);

  return (
    <div className="min-h-screen bg-background">
      <NavHeader />
      
      <main className="container mx-auto px-4 py-8">
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Signal Feed</h1>
            <p className="text-muted-foreground">
              Real-time market narratives ranked by acceleration and probability.
            </p>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={loadSignals}
            disabled={loading}
            className="gap-2"
          >
            <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
            Refresh
          </Button>
        </div>

        {usingMockData && (
          <div className="mb-6 p-4 rounded-lg border border-ghost-amber/20 bg-ghost-amber/5 flex items-center gap-3">
            <AlertCircle className="h-5 w-5 text-ghost-amber" />
            <div>
              <p className="font-medium text-ghost-amber">Using Demo Data</p>
              <p className="text-sm text-muted-foreground">
                Backend API unavailable. Showing mock data for demonstration.
              </p>
            </div>
          </div>
        )}

        <div className="flex flex-col lg:flex-row gap-4 mb-6">
          <div className="flex flex-wrap gap-2">
            {statusFilters.map((filter) => {
              const Icon = filter.icon;
              const isActive = statusFilter === filter.value;
              const count = statusCounts[filter.value] || 0;
              
              return (
                <Button
                  key={filter.value}
                  variant={isActive ? "default" : "outline"}
                  size="sm"
                  onClick={() => setStatusFilter(filter.value)}
                  className={cn(
                    "gap-2",
                    !isActive && "text-muted-foreground"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {filter.label}
                  <span className={cn(
                    "text-xs px-1.5 py-0.5 rounded-full",
                    isActive ? "bg-primary-foreground/20" : "bg-muted"
                  )}>
                    {count}
                  </span>
                </Button>
              );
            })}
          </div>
          
          <div className="flex items-center gap-2 lg:ml-auto">
            <div className="flex items-center border border-border rounded-md overflow-hidden">
              {([
                { value: 'all', label: 'All' },
                { value: 'narrative', label: 'Narratives' },
                { value: 'prediction', label: 'Markets' },
              ] as const).map((lane) => (
                <Button
                  key={lane.value}
                  variant={laneFilter === lane.value ? 'secondary' : 'ghost'}
                  size="sm"
                  onClick={() => setLaneFilter(lane.value)}
                  className="rounded-none"
                >
                  {lane.label}
                </Button>
              ))}
            </div>
            <span className="text-sm text-muted-foreground">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-muted border border-border rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {sortOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            
            <div className="hidden sm:flex items-center border border-border rounded-md overflow-hidden">
              <Button
                variant={viewMode === 'default' ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('default')}
                className="rounded-none"
              >
                <LayoutGrid className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'compact' ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('compact')}
                className="rounded-none"
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-40 bg-muted/50 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredAndSortedSignals.length === 0 ? (
              signals.length === 0 ? (
                <div className="text-center py-20">
                  <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-muted mb-5">
                    <Sparkles className="h-7 w-7 text-muted-foreground" />
                  </div>
                  <h2 className="text-lg font-semibold mb-2">No live signals yet</h2>
                  <p className="text-muted-foreground max-w-md mx-auto mb-6">
                    Ghost is gathering and analyzing data across sources. Fresh
                    signals appear here as narratives accelerate.
                  </p>
                  <Button variant="outline" onClick={loadSignals} className="gap-2">
                    <RefreshCw className="h-4 w-4" />
                    Refresh
                  </Button>
                </div>
              ) : (
                <div className="text-center py-16 text-muted-foreground">
                  <p>No signals match the selected filter.</p>
                </div>
              )
            ) : (
              filteredAndSortedSignals.map((signal) => (
                <SignalCard 
                  key={signal.id} 
                  signal={signal} 
                  variant={viewMode}
                />
              ))
            )}
          </div>
        )}

        <div className="mt-12 pt-8 border-t border-border">
          <FinancialDisclaimer variant="card" />
        </div>
      </main>
    </div>
  );
}
