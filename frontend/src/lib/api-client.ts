/**
 * Ghost API Client
 *
 * Connects the frontend to the FastAPI backend. Only ever returns real
 * backend data — there is no demo/mock fallback.
 */

import type { Signal } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiHealth {
  status: string;
  timestamp: string;
  // Source keys are dynamic (youtube, polymarket, stocktwits, news, polygon, reddit, ...).
  sources: Record<string, boolean>;
  database: string;
}

interface ApiStats {
  content_items: number;
  ticker_mentions: number;
  signals_cached: number;
  cache_age_seconds: number | null;
}

class GhostApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async fetch<T>(endpoint: string, options?: RequestInit, timeoutMs: number = 120000): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.warn(`API request timed out after ${timeoutMs}ms`);
      } else {
        console.warn(`API request failed:`, error);
      }
      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  async checkHealth(): Promise<ApiHealth | null> {
    try {
      return await this.fetch<ApiHealth>('/health');
    } catch {
      return null;
    }
  }

  async getStats(): Promise<ApiStats | null> {
    try {
      return await this.fetch<ApiStats>('/api/stats');
    } catch {
      return null;
    }
  }

  async getSignals(status?: string): Promise<Signal[]> {
    try {
      const params = status ? `?status=${status}` : '';
      return await this.fetch<Signal[]>(`/api/signals${params}`);
    } catch {
      // No demo fallback — return nothing so only real signals ever show.
      return [];
    }
  }

  async getSignal(id: string): Promise<Signal | null> {
    try {
      return await this.fetch<Signal>(`/api/signals/${id}`);
    } catch {
      return null;
    }
  }

  async searchSignals(query: string): Promise<Signal[]> {
    try {
      return await this.fetch<Signal[]>(`/api/search?q=${encodeURIComponent(query)}`);
    } catch {
      return [];
    }
  }

  async triggerScrape(): Promise<{ status: string; message: string }> {
    try {
      return await this.fetch('/api/scrape', { method: 'POST' });
    } catch {
      return { status: 'error', message: 'API unavailable' };
    }
  }
}

export const apiClient = new GhostApiClient();
export default apiClient;
