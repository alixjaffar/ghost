"use client";

import { cn } from "@/lib/utils";

interface GhostLogoProps {
  size?: "sm" | "md" | "lg" | "xl";
  showText?: boolean;
  className?: string;
}

const sizeConfig = {
  sm: { icon: 24, text: "text-lg" },
  md: { icon: 32, text: "text-xl" },
  lg: { icon: 48, text: "text-2xl" },
  xl: { icon: 64, text: "text-4xl" },
};

export function GhostLogo({ size = "md", showText = true, className }: GhostLogoProps) {
  const config = sizeConfig[size];

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <svg 
        width={config.icon} 
        height={config.icon} 
        viewBox="0 0 48 48" 
        fill="none"
        className="shrink-0"
      >
        <path
          d="M24 4C14.059 4 6 12.059 6 22v18c0 2.2 1.8 4 4 4h2c1.1 0 2-.9 2-2v-4c0-1.1.9-2 2-2s2 .9 2 2v4c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2v-4c0-1.1.9-2 2-2s2 .9 2 2v4c0 1.1.9 2 2 2h2c2.2 0 4-1.8 4-4V22c0-9.941-8.059-18-18-18z"
          fill="currentColor"
          className="text-foreground"
        />
        <ellipse cx="17" cy="22" rx="3" ry="4" fill="currentColor" className="text-background" />
        <ellipse cx="31" cy="22" rx="3" ry="4" fill="currentColor" className="text-background" />
      </svg>
      {showText && (
        <span className={cn("font-bold tracking-tight", config.text)}>
          GHOST
        </span>
      )}
    </div>
  );
}
