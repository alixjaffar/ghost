"use client";

import { cn } from "@/lib/utils";
import { TrendingUp } from "lucide-react";

interface AccelerationScoreProps {
  score: number;
  size?: "sm" | "md" | "lg";
  showIcon?: boolean;
  className?: string;
}

export function AccelerationScore({ 
  score, 
  size = "md", 
  showIcon = true,
  className 
}: AccelerationScoreProps) {
  const getColor = (val: number) => {
    if (val >= 80) return "text-ghost-green";
    if (val >= 60) return "text-ghost-amber";
    return "text-muted-foreground";
  };

  const getBgColor = (val: number) => {
    if (val >= 80) return "bg-ghost-green/10";
    if (val >= 60) return "bg-ghost-amber/10";
    return "bg-muted/50";
  };

  const sizeClasses = {
    sm: "text-sm px-2 py-0.5 gap-1",
    md: "text-base px-3 py-1 gap-1.5",
    lg: "text-xl px-4 py-2 gap-2",
  };

  const iconSizes = {
    sm: "h-3 w-3",
    md: "h-4 w-4",
    lg: "h-5 w-5",
  };

  return (
    <div 
      className={cn(
        "inline-flex items-center rounded-md font-semibold tabular-nums",
        sizeClasses[size],
        getBgColor(score),
        getColor(score),
        className
      )}
    >
      {showIcon && <TrendingUp className={iconSizes[size]} />}
      <span>{score}</span>
      <span className="text-muted-foreground font-normal">/100</span>
    </div>
  );
}
