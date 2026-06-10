"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { NavHeader } from "@/components/layout/nav-header";
import { SignalCard, FinancialDisclaimer } from "@/components/ghost";
import { Button } from "@/components/ui/button";
import { useWatchlist } from "@/lib/watchlist";
import { apiClient } from "@/lib/api-client";
import type { Signal } from "@/lib/types";
import { Bookmark, Plus, Ghost } from "lucide-react";

export default function WatchlistPage() {
  const { items, isLoaded } = useWatchlist();
  const [allSignals, setAllSignals] = useState<Signal[]>([]);
  const [signalsLoaded, setSignalsLoaded] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const signals = await apiClient.getSignals();
      if (!cancelled) {
        setAllSignals(signals);
        setSignalsLoaded(true);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const watchedSignals = useMemo(() => {
    const signalIds = items
      .filter(item => item.type === 'signal')
      .map(item => item.id);
    return allSignals.filter(signal => signalIds.includes(signal.id));
  }, [items, allSignals]);

  const watchedTickers = useMemo(() => {
    const tickerIds = items
      .filter(item => item.type === 'ticker')
      .map(item => item.id);

    const tickers: Map<string, { symbol: string; signals: Signal[] }> = new Map();

    allSignals.forEach(signal => {
      signal.relatedTickers.forEach(ticker => {
        if (tickerIds.includes(ticker.symbol)) {
          const existing = tickers.get(ticker.symbol);
          if (existing) {
            existing.signals.push(signal);
          } else {
            tickers.set(ticker.symbol, { symbol: ticker.symbol, signals: [signal] });
          }
        }
      });
    });

    return Array.from(tickers.values());
  }, [items, allSignals]);

  if (!isLoaded || !signalsLoaded) {
    return (
      <div className="min-h-screen bg-background">
        <NavHeader />
        <main className="container mx-auto px-4 py-8">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-48" />
            <div className="h-4 bg-muted rounded w-64" />
            <div className="space-y-4 mt-8">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-32 bg-muted rounded-xl" />
              ))}
            </div>
          </div>
        </main>
      </div>
    );
  }

  const isEmpty = watchedSignals.length === 0 && watchedTickers.length === 0;

  return (
    <div className="min-h-screen bg-background">
      <NavHeader />
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Watchlist</h1>
          <p className="text-muted-foreground">
            Signals and tickers you&apos;re tracking.
          </p>
        </div>

        {isEmpty ? (
          <div className="text-center py-20">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-6">
              <Bookmark className="h-8 w-8 text-muted-foreground" />
            </div>
            <h2 className="text-xl font-semibold mb-2">Your watchlist is empty</h2>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Start tracking signals by clicking the bookmark icon on any signal card.
            </p>
            <Link href="/signals">
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                Browse Signals
              </Button>
            </Link>
          </div>
        ) : (
          <div className="space-y-12">
            {watchedSignals.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Ghost className="h-5 w-5" />
                  Watched Signals
                  <span className="text-sm font-normal text-muted-foreground">
                    ({watchedSignals.length})
                  </span>
                </h2>
                <div className="space-y-4">
                  {watchedSignals.map(signal => (
                    <SignalCard key={signal.id} signal={signal} />
                  ))}
                </div>
              </section>
            )}

            {watchedTickers.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold mb-4">
                  Watched Tickers
                  <span className="text-sm font-normal text-muted-foreground ml-2">
                    ({watchedTickers.length})
                  </span>
                </h2>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {watchedTickers.map(({ symbol, signals }) => (
                    <div 
                      key={symbol}
                      className="p-4 rounded-xl border border-border bg-card"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xl font-bold">${symbol}</span>
                        <span className="text-sm text-muted-foreground">
                          {signals.length} related signal{signals.length !== 1 ? 's' : ''}
                        </span>
                      </div>
                      <div className="space-y-2">
                        {signals.slice(0, 2).map(signal => (
                          <Link 
                            key={signal.id}
                            href={`/signals/${signal.id}`}
                            className="block text-sm text-muted-foreground hover:text-foreground transition-colors"
                          >
                            {signal.title}
                          </Link>
                        ))}
                        {signals.length > 2 && (
                          <span className="text-xs text-muted-foreground">
                            +{signals.length - 2} more
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        )}

        {!isEmpty && (
          <div className="mt-12 pt-8 border-t border-border">
            <FinancialDisclaimer variant="card" />
          </div>
        )}
      </main>
    </div>
  );
}
