"use client";

import { cn } from "@/lib/utils";
import type { SignalStatus } from "@/lib/types";
import { getStatusColor, getStatusBgColor } from "@/lib/types";
import { Zap, TrendingUp, Sparkles, TrendingDown } from "lucide-react";

interface StatusBadgeProps {
  status: SignalStatus;
  size?: "sm" | "md";
  className?: string;
}

const statusConfig = {
  breaking: { label: "Breaking", Icon: Zap },
  accelerating: { label: "Accelerating", Icon: TrendingUp },
  emerging: { label: "Emerging", Icon: Sparkles },
  cooling: { label: "Cooling", Icon: TrendingDown },
};

export function StatusBadge({ status, size = "md", className }: StatusBadgeProps) {
  const { label, Icon } = statusConfig[status];
  
  const sizeClasses = {
    sm: "text-[10px] px-1.5 py-0.5 gap-0.5",
    md: "text-xs px-2 py-1 gap-1",
  };

  const iconSizes = {
    sm: "h-2.5 w-2.5",
    md: "h-3 w-3",
  };

  return (
    <div 
      className={cn(
        "inline-flex items-center rounded border font-medium uppercase tracking-wider",
        sizeClasses[size],
        getStatusBgColor(status),
        getStatusColor(status),
        className
      )}
    >
      <Icon className={iconSizes[size]} />
      <span>{label}</span>
    </div>
  );
}
