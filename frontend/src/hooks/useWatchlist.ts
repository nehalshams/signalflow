import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { addToWatchlist, getWatchlist, removeFromWatchlist } from "@/lib/stocks";
import type { WatchlistItem } from "@/lib/stocks";

const WATCHLIST_KEY = ["watchlist"] as const;

export function useWatchlist() {
  return useQuery<WatchlistItem[]>({
    queryKey: WATCHLIST_KEY,
    queryFn: getWatchlist,
  });
}

export function useAddToWatchlist() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (stockId: number) => addToWatchlist(stockId),
    onSuccess: () => qc.invalidateQueries({ queryKey: WATCHLIST_KEY }),
  });
}

export function useRemoveFromWatchlist() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (stockId: number) => removeFromWatchlist(stockId),
    onSuccess: () => qc.invalidateQueries({ queryKey: WATCHLIST_KEY }),
  });
}
