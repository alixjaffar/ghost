"use client";

import { cn } from "@/lib/utils";

interface ProbabilityRingProps {
  value: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  className?: string;
}

const sizeConfig = {
  sm: { size: 48, stroke: 4, fontSize: "text-xs" },
  md: { size: 80, stroke: 6, fontSize: "text-lg" },
  lg: { size: 120, stroke: 8, fontSize: "text-2xl" },
};

export function ProbabilityRing({ 
  value, 
  size = "md", 
  showLabel = true,
  className 
}: ProbabilityRingProps) {
  const config = sizeConfig[size];
  const radius = (config.size - config.stroke) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (value / 100) * circumference;

  const getColor = (val: number) => {
    if (val >= 75) return "stroke-[oklch(0.75_0.15_145)]";
    if (val >= 50) return "stroke-[oklch(0.75_0.15_85)]";
    return "stroke-[oklch(0.55_0_0)]";
  };

  return (
    <div className={cn("relative inline-flex items-center justify-center", className)}>
      <svg
        width={config.size}
        height={config.size}
        className="transform -rotate-90"
      >
        <circle
          cx={config.size / 2}
          cy={config.size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={config.stroke}
          className="text-muted/30"
        />
        <circle
          cx={config.size / 2}
          cy={config.size / 2}
          r={radius}
          fill="none"
          strokeWidth={config.stroke}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={cn("transition-all duration-500", getColor(value))}
        />
      </svg>
      {showLabel && (
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={cn("font-bold tabular-nums", config.fontSize)}>
            {value}%
          </span>
          {size !== "sm" && (
            <span className="text-[10px] text-muted-foreground uppercase tracking-wider">
              Probability
            </span>
          )}
        </div>
      )}
    </div>
  );
}
