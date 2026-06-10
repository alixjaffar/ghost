"use client";

import { cn } from "@/lib/utils";
import type { ConfidenceLevel } from "@/lib/types";
import { getConfidenceLabel } from "@/lib/types";
import { Shield, ShieldCheck, ShieldAlert } from "lucide-react";

interface ConfidenceBadgeProps {
  confidence: ConfidenceLevel;
  size?: "sm" | "md";
  showIcon?: boolean;
  className?: string;
}

const confidenceConfig = {
  very_high: { Icon: ShieldCheck, color: "text-ghost-green" },
  high: { Icon: ShieldCheck, color: "text-ghost-green" },
  medium: { Icon: Shield, color: "text-ghost-amber" },
  low: { Icon: ShieldAlert, color: "text-muted-foreground" },
};

export function ConfidenceBadge({ 
  confidence, 
  size = "md", 
  showIcon = true,
  className 
}: ConfidenceBadgeProps) {
  const { Icon, color } = confidenceConfig[confidence];
  const label = getConfidenceLabel(confidence);
  
  const sizeClasses = {
    sm: "text-[10px] gap-0.5",
    md: "text-xs gap-1",
  };

  const iconSizes = {
    sm: "h-2.5 w-2.5",
    md: "h-3 w-3",
  };

  return (
    <div 
      className={cn(
        "inline-flex items-center text-muted-foreground",
        sizeClasses[size],
        className
      )}
    >
      {showIcon && <Icon className={cn(iconSizes[size], color)} />}
      <span>{label} Confidence</span>
    </div>
  );
}
