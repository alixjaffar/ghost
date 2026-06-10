"use client";

import { Area, AreaChart, ResponsiveContainer, YAxis } from "recharts";
import type { VelocityDataPoint } from "@/lib/types";
import { cn } from "@/lib/utils";

interface VelocityChartProps {
  data: VelocityDataPoint[];
  height?: number;
  showGradient?: boolean;
  color?: "green" | "red" | "neutral";
  className?: string;
}

const colorConfig = {
  green: {
    stroke: "oklch(0.75 0.15 145)",
    fill: "url(#velocityGradientGreen)",
  },
  red: {
    stroke: "oklch(0.65 0.18 25)",
    fill: "url(#velocityGradientRed)",
  },
  neutral: {
    stroke: "oklch(0.55 0 0)",
    fill: "url(#velocityGradientNeutral)",
  },
};

export function VelocityChart({ 
  data, 
  height = 40,
  showGradient = true,
  color = "green",
  className 
}: VelocityChartProps) {
  const config = colorConfig[color];
  
  const minValue = Math.min(...data.map(d => d.value));
  const maxValue = Math.max(...data.map(d => d.value));
  const padding = (maxValue - minValue) * 0.1;

  return (
    <div className={cn("w-full", className)} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 2, right: 0, left: 0, bottom: 2 }}>
          <defs>
            <linearGradient id="velocityGradientGreen" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="oklch(0.75 0.15 145)" stopOpacity={0.3} />
              <stop offset="100%" stopColor="oklch(0.75 0.15 145)" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="velocityGradientRed" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="oklch(0.65 0.18 25)" stopOpacity={0.3} />
              <stop offset="100%" stopColor="oklch(0.65 0.18 25)" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="velocityGradientNeutral" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="oklch(0.55 0 0)" stopOpacity={0.3} />
              <stop offset="100%" stopColor="oklch(0.55 0 0)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <YAxis 
            domain={[minValue - padding, maxValue + padding]} 
            hide 
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke={config.stroke}
            strokeWidth={1.5}
            fill={showGradient ? config.fill : "transparent"}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
