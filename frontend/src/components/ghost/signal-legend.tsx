"use client";

import { useState } from "react";
import { HelpCircle, X, Zap, TrendingUp, Sparkles, TrendingDown, Target, Gauge, Shield, MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const statusInfo = [
  {
    status: "Breaking",
    icon: Zap,
    color: "text-ghost-red",
    bg: "bg-ghost-red/10",
    criteria: "Acceleration ≥85 AND 24h change ≥30%",
    meaning: "Narrative is exploding right now. Highest urgency.",
  },
  {
    status: "Accelerating",
    icon: TrendingUp,
    color: "text-ghost-amber",
    bg: "bg-ghost-amber/10",
    criteria: "Acceleration ≥70 OR 24h change ≥20%",
    meaning: "Gaining significant momentum. Worth close monitoring.",
  },
  {
    status: "Emerging",
    icon: Sparkles,
    color: "text-ghost-blue",
    bg: "bg-ghost-blue/10",
    criteria: "Acceleration ≥50 OR 24h change ≥0%",
    meaning: "New narrative forming. Early stage signal.",
  },
  {
    status: "Cooling",
    icon: TrendingDown,
    color: "text-muted-foreground",
    bg: "bg-muted/50",
    criteria: "Below acceleration/change thresholds",
    meaning: "Narrative is fading or stabilizing.",
  },
];

const metricInfo = [
  {
    name: "Event Probability",
    icon: Target,
    description: "Estimated likelihood (20-95%) that the narrative will materialize into a significant market event.",
  },
  {
    name: "Acceleration Score",
    icon: Gauge,
    description: "How fast mentions are increasing (0-100). Compares recent activity to historical average.",
  },
  {
    name: "Confidence Level",
    icon: Shield,
    description: "Data quality based on mention volume and source diversity.",
  },
];

export function SignalLegend() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Floating Chat Button */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full shadow-lg",
          "bg-ghost-green hover:bg-ghost-green/90 text-black",
          "transition-all duration-200",
          isOpen && "scale-0 opacity-0"
        )}
      >
        <MessageCircle className="h-6 w-6" />
      </Button>

      {/* Chat Popup */}
      <div
        className={cn(
          "fixed bottom-6 right-6 z-50 w-[380px] max-h-[70vh]",
          "rounded-2xl border border-border bg-card shadow-2xl",
          "transition-all duration-300 origin-bottom-right",
          isOpen ? "scale-100 opacity-100" : "scale-0 opacity-0 pointer-events-none"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border bg-ghost-green/10 rounded-t-2xl">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-ghost-green/20 flex items-center justify-center">
              <HelpCircle className="h-4 w-4 text-ghost-green" />
            </div>
            <div>
              <h3 className="font-semibold text-sm">Signal Legend</h3>
              <p className="text-xs text-muted-foreground">How to read signals</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsOpen(false)}
            className="h-8 w-8 p-0 rounded-full hover:bg-background/50"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4 overflow-y-auto max-h-[calc(70vh-80px)]">
          {/* Status Section */}
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
              Signal Status
            </p>
            <div className="space-y-2">
              {statusInfo.map((item) => {
                const Icon = item.icon;
                return (
                  <div
                    key={item.status}
                    className={cn("p-2.5 rounded-lg", item.bg)}
                  >
                    <div className="flex items-center gap-2">
                      <Icon className={cn("h-4 w-4 shrink-0", item.color)} />
                      <div className="min-w-0">
                        <span className={cn("font-medium text-sm", item.color)}>
                          {item.status}
                        </span>
                        <p className="text-xs text-muted-foreground truncate">
                          {item.meaning}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Metrics Section */}
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
              Key Metrics
            </p>
            <div className="space-y-2">
              {metricInfo.map((item) => {
                const Icon = item.icon;
                return (
                  <div
                    key={item.name}
                    className="p-2.5 rounded-lg bg-muted/30"
                  >
                    <div className="flex items-start gap-2">
                      <Icon className="h-4 w-4 text-ghost-green shrink-0 mt-0.5" />
                      <div>
                        <span className="font-medium text-sm">{item.name}</span>
                        <p className="text-xs text-muted-foreground">
                          {item.description}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Disclaimer */}
          <div className="p-2.5 rounded-lg border border-ghost-amber/20 bg-ghost-amber/5">
            <p className="text-xs text-muted-foreground">
              <strong className="text-ghost-amber">Note:</strong> These metrics measure social media momentum, not guaranteed market outcomes.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
