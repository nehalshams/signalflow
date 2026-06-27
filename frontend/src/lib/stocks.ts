import { apiFetch } from "./api";

export type Stock = {
  id: number;
  symbol: string;
  company_name: string;
  sector: string;
  exchange: string;
  is_active: boolean;
};

export type WatchlistItem = {
  id: number;
  stock: Stock;
  added_at: string;
};

// Yahoo Finance suffixes per exchange — mirrors the backend's to_yf_ticker.
const EXCHANGE_SUFFIX: Record<string, string> = { NSE: ".NS", BSE: ".BO" };

/** Map a bare symbol + exchange to its Yahoo Finance ticker (RELIANCE -> RELIANCE.NS). */
export function toYahooTicker(symbol: string, exchange: string): string {
  return `${symbol}${EXCHANGE_SUFFIX[exchange] ?? ""}`;
}

/** GET /stocks/search/?q= — search the local stock universe (public). */
export function searchStocks(query: string): Promise<Stock[]> {
  return apiFetch<Stock[]>(`/stocks/search/?q=${encodeURIComponent(query)}`, {
    auth: false,
  });
}

/** GET /watchlist/ — the signed-in user's watchlist. */
export function getWatchlist(): Promise<WatchlistItem[]> {
  return apiFetch<WatchlistItem[]>("/watchlist/");
}

/** POST /watchlist/ — add a stock by its primary key. */
export function addToWatchlist(stockId: number): Promise<WatchlistItem> {
  return apiFetch<WatchlistItem>("/watchlist/", {
    method: "POST",
    body: { stock_id: stockId },
  });
}

/** DELETE /watchlist/<stockId>/ — remove a stock from the watchlist. */
export function removeFromWatchlist(stockId: number): Promise<void> {
  return apiFetch<void>(`/watchlist/${stockId}/`, { method: "DELETE" });
}
