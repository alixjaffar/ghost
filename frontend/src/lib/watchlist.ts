"use client";

import { useState, useCallback, useSyncExternalStore } from 'react';
import type { WatchlistItem } from './types';

const WATCHLIST_KEY = 'ghost-watchlist';

let listeners: Array<() => void> = [];
let cachedItems: WatchlistItem[] = [];
let cacheInitialized = false;
const serverSnapshot: WatchlistItem[] = []; // Stable reference for SSR

function emitChange() {
  updateCache();
  for (const listener of listeners) {
    listener();
  }
}

function subscribe(listener: () => void) {
  listeners = [...listeners, listener];
  return () => {
    listeners = listeners.filter(l => l !== listener);
  };
}

function updateCache(): void {
  if (typeof window === 'undefined') {
    cachedItems = [];
    return;
  }
  try {
    const stored = localStorage.getItem(WATCHLIST_KEY);
    cachedItems = stored ? JSON.parse(stored) : [];
    cacheInitialized = true;
  } catch {
    cachedItems = [];
  }
}

function getSnapshot(): WatchlistItem[] {
  if (!cacheInitialized && typeof window !== 'undefined') {
    updateCache();
  }
  return cachedItems;
}

function getServerSnapshot(): WatchlistItem[] {
  return serverSnapshot;
}

export function getWatchlist(): WatchlistItem[] {
  return getSnapshot();
}

export function saveWatchlist(items: WatchlistItem[]): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(WATCHLIST_KEY, JSON.stringify(items));
    emitChange();
  } catch (e) {
    console.error('Failed to save watchlist:', e);
  }
}

export function addToWatchlist(type: 'signal' | 'ticker', id: string): WatchlistItem[] {
  const items = getWatchlist();
  if (items.some(item => item.type === type && item.id === id)) {
    return items;
  }
  const newItems = [...items, { type, id, addedAt: new Date().toISOString() }];
  saveWatchlist(newItems);
  return newItems;
}

export function removeFromWatchlist(type: 'signal' | 'ticker', id: string): WatchlistItem[] {
  const items = getWatchlist();
  const newItems = items.filter(item => !(item.type === type && item.id === id));
  saveWatchlist(newItems);
  return newItems;
}

export function isInWatchlist(type: 'signal' | 'ticker', id: string): boolean {
  const items = getWatchlist();
  return items.some(item => item.type === type && item.id === id);
}

export function useWatchlist() {
  const items = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
  
  const [isLoaded] = useState(() => {
    return typeof window !== 'undefined';
  });

  const add = useCallback((type: 'signal' | 'ticker', id: string) => {
    addToWatchlist(type, id);
  }, []);

  const remove = useCallback((type: 'signal' | 'ticker', id: string) => {
    removeFromWatchlist(type, id);
  }, []);

  const toggle = useCallback((type: 'signal' | 'ticker', id: string) => {
    if (isInWatchlist(type, id)) {
      remove(type, id);
    } else {
      add(type, id);
    }
  }, [add, remove]);

  const isWatched = useCallback((type: 'signal' | 'ticker', id: string) => {
    return items.some(item => item.type === type && item.id === id);
  }, [items]);

  return {
    items,
    isLoaded,
    add,
    remove,
    toggle,
    isWatched,
  };
}
