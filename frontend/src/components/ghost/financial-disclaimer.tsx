"use client";

import { cn } from "@/lib/utils";
import { AlertTriangle } from "lucide-react";

interface FinancialDisclaimerProps {
  variant?: "inline" | "card";
  className?: string;
}

export function FinancialDisclaimer({ variant = "inline", className }: FinancialDisclaimerProps) {
  if (variant === "card") {
    return (
      <div className={cn(
        "rounded-lg border border-ghost-amber/20 bg-ghost-amber/5 p-4",
        className
      )}>
        <div className="flex gap-3">
          <AlertTriangle className="h-5 w-5 text-ghost-amber shrink-0 mt-0.5" />
          <div className="space-y-2 text-sm">
            <p className="font-medium text-ghost-amber">Important Disclaimer</p>
            <p className="text-muted-foreground">
              Ghost provides informational signals based on aggregated internet activity. 
              Event probabilities, acceleration scores, and confidence levels are algorithmic estimates 
              for demonstration purposes only — not predictions or guarantees of future events.
            </p>
            <p className="text-muted-foreground">
              This is not financial advice. Do not make investment decisions based solely on this information. 
              Always conduct your own research and consult qualified financial advisors before investing.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <p className={cn(
      "text-xs text-muted-foreground flex items-center gap-1.5",
      className
    )}>
      <AlertTriangle className="h-3 w-3 text-ghost-amber" />
      <span>
        Demo estimates only. Not financial advice.
      </span>
    </p>
  );
}
