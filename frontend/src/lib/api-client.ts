/**
 * Ghost API Client
 * 
 * Connects the frontend to the FastAPI backend.
 * Falls back to mock data if the API is unavailable.
 */

import type { Signal } from './types';
import { mockSignals, getSignalById as getMockSignalById, searchSignals as searchMockSignals } from './mock-data';

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
  private useMockData: boolean = false;

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
        console.warn(`API request timed out after ${timeoutMs}ms, using mock data`);
      } else {
        console.warn(`API request failed, using mock data:`, error);
      }
      this.useMockData = true;
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
      const signals = await this.fetch<Signal[]>(`/api/signals${params}`);
      this.useMockData = false;
      return signals;
    } catch {
      console.log('Using mock signals data');
      return status 
        ? mockSignals.filter(s => s.status === status)
        : mockSignals;
    }
  }

  async getSignal(id: string): Promise<Signal | null> {
    try {
      const signal = await this.fetch<Signal>(`/api/signals/${id}`);
      this.useMockData = false;
      return signal;
    } catch {
      console.log('Using mock signal data for:', id);
      return getMockSignalById(id) || null;
    }
  }

  async searchSignals(query: string): Promise<Signal[]> {
    try {
      const signals = await this.fetch<Signal[]>(`/api/search?q=${encodeURIComponent(query)}`);
      this.useMockData = false;
      return signals;
    } catch {
      console.log('Using mock search data');
      return searchMockSignals(query);
    }
  }

  async triggerScrape(): Promise<{ status: string; message: string }> {
    try {
      return await this.fetch('/api/scrape', { method: 'POST' });
    } catch {
      return { status: 'error', message: 'API unavailable' };
    }
  }

  isUsingMockData(): boolean {
    return this.useMockData;
  }
}

export const apiClient = new GhostApiClient();
export default apiClient;
