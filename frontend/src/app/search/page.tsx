"use client";

import { useState, useEffect } from "react";
import { NavHeader } from "@/components/layout/nav-header";
import { SignalCard, FinancialDisclaimer } from "@/components/ghost";
import { Input } from "@/components/ui/input";
import { apiClient } from "@/lib/api-client";
import type { Signal } from "@/lib/types";
import { Search, TrendingUp, Sparkles, Loader2 } from "lucide-react";

const popularSearches = [
  "AI",
  "chips",
  "energy",
  "GLP-1",
  "nuclear",
  "NVDA",
  "shipping",
  "copper",
];

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Signal[]>([]);
  const [topSignals, setTopSignals] = useState<Signal[]>([]);
  const [emergingSignals, setEmergingSignals] = useState<Signal[]>([]);
  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadInitialData() {
      setLoading(true);
      try {
        const all = await apiClient.getSignals();
        setTopSignals(
          [...all]
            .sort((a, b) => b.accelerationScore - a.accelerationScore)
            .slice(0, 3)
        );
        setEmergingSignals(
          all.filter(s => s.status === 'emerging').slice(0, 3)
        );
      } catch (error) {
        console.error('Failed to load signals:', error);
      } finally {
        setLoading(false);
      }
    }
    loadInitialData();
  }, []);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setSearching(true);
      try {
        const data = await apiClient.searchSignals(query);
        setResults(data);
      } catch (error) {
        console.error('Search failed:', error);
      } finally {
        setSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  const allTickers = topSignals.flatMap(s => s.relatedTickers.map(t => t.symbol));
  const uniqueTickers = [...new Set(allTickers)].sort();

  const matchingTickers = query.trim() 
    ? uniqueTickers.filter(t => t.toLowerCase().includes(query.toLowerCase()))
    : [];

  return (
    <div className="min-h-screen bg-background">
      <NavHeader />
      
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-4">Search</h1>
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search signals, tickers, narratives..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="pl-12 py-6 text-lg"
              autoFocus
            />
            {searching && (
              <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground animate-spin" />
            )}
          </div>
        </div>

        {!query.trim() ? (
          <div className="space-y-8">
            <section>
              <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
                Popular Searches
              </h2>
              <div className="flex flex-wrap gap-2">
                {popularSearches.map(term => (
                  <button
                    key={term}
                    onClick={() => setQuery(term)}
                    className="px-4 py-2 rounded-lg border border-border bg-card hover:bg-accent transition-colors text-sm"
                  >
                    {term}
                  </button>
                ))}
              </div>
            </section>

            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-24 bg-muted/50 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : (
              <>
                <section>
                  <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    Top Accelerating
                  </h2>
                  <div className="space-y-3">
                    {topSignals.map(signal => (
                      <SignalCard key={signal.id} signal={signal} variant="compact" />
                    ))}
                  </div>
                </section>

                <section>
                  <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
                    <Sparkles className="h-4 w-4" />
                    Recently Emerging
                  </h2>
                  <div className="space-y-3">
                    {emergingSignals.map(signal => (
                      <SignalCard key={signal.id} signal={signal} variant="compact" />
                    ))}
                  </div>
                </section>
              </>
            )}
          </div>
        ) : (
          <div className="space-y-8">
            {matchingTickers.length > 0 && (
              <section>
                <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
                  Tickers ({matchingTickers.length})
                </h2>
                <div className="flex flex-wrap gap-2">
                  {matchingTickers.map(ticker => (
                    <button
                      key={ticker}
                      onClick={() => setQuery(ticker)}
                      className="px-4 py-2 rounded-lg border border-border bg-card hover:bg-accent transition-colors font-medium"
                    >
                      ${ticker}
                    </button>
                  ))}
                </div>
              </section>
            )}

            <section>
              <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
                Signals ({results.length})
              </h2>
              {searching ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
                  <p>Searching...</p>
                </div>
              ) : results.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <p>No signals found for &quot;{query}&quot;</p>
                  <p className="text-sm mt-2">Try a different search term or browse all signals.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {results.map(signal => (
                    <SignalCard key={signal.id} signal={signal} />
                  ))}
                </div>
              )}
            </section>
          </div>
        )}

        <div className="mt-12 pt-8 border-t border-border">
          <FinancialDisclaimer />
        </div>
      </main>
    </div>
  );
}
