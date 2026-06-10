"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Bookmark, BookmarkCheck } from "lucide-react";
import { useWatchlist } from "@/lib/watchlist";

interface WatchlistButtonProps {
  type: 'signal' | 'ticker';
  id: string;
  size?: "sm" | "md" | "lg";
  variant?: "default" | "ghost" | "outline";
  showLabel?: boolean;
  className?: string;
}

export function WatchlistButton({ 
  type,
  id,
  size = "md",
  variant = "ghost",
  showLabel = false,
  className 
}: WatchlistButtonProps) {
  const { isWatched, toggle, isLoaded } = useWatchlist();
  const watched = isLoaded && isWatched(type, id);

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    toggle(type, id);
  };

  const sizeClasses = {
    sm: "h-7 w-7",
    md: "h-9 w-9",
    lg: "h-11 w-11",
  };

  const iconSizes = {
    sm: "h-3.5 w-3.5",
    md: "h-4 w-4",
    lg: "h-5 w-5",
  };

  if (showLabel) {
    return (
      <Button
        variant={variant}
        size={size === "sm" ? "sm" : size === "lg" ? "lg" : "default"}
        onClick={handleClick}
        className={cn(
          "gap-2",
          watched && "text-ghost-amber",
          className
        )}
      >
        {watched ? (
          <BookmarkCheck className={iconSizes[size]} />
        ) : (
          <Bookmark className={iconSizes[size]} />
        )}
        {watched ? "Watching" : "Watch"}
      </Button>
    );
  }

  return (
    <Button
      variant={variant}
      size="icon"
      onClick={handleClick}
      className={cn(
        sizeClasses[size],
        watched && "text-ghost-amber",
        className
      )}
      aria-label={watched ? "Remove from watchlist" : "Add to watchlist"}
    >
      {watched ? (
        <BookmarkCheck className={iconSizes[size]} />
      ) : (
        <Bookmark className={iconSizes[size]} />
      )}
    </Button>
  );
}
