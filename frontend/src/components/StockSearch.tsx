import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Check, Loader2, Plus, Search } from "lucide-react";
import { toast } from "sonner";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ApiError } from "@/lib/api";
import { searchStocks, toYahooTicker } from "@/lib/stocks";
import type { Stock } from "@/lib/stocks";
import { useAddToWatchlist, useWatchlist } from "@/hooks/useWatchlist";

export function StockSearch() {
  const [query, setQuery] = useState("");
  const [debounced, setDebounced] = useState("");

  // debounce keystrokes so we don't hit the API on every character
  useEffect(() => {
    const t = setTimeout(() => setDebounced(query.trim()), 300);
    return () => clearTimeout(t);
  }, [query]);

  const { data: results = [], isFetching } = useQuery<Stock[]>({
    queryKey: ["search", debounced],
    queryFn: () => searchStocks(debounced),
    enabled: debounced.length > 0,
  });

  const { data: watchlist = [] } = useWatchlist();
  const watchedIds = new Set(watchlist.map((w) => w.stock.id));
  const add = useAddToWatchlist();

  function handleAdd(stock: Stock) {
    add.mutate(stock.id, {
      onSuccess: () => toast.success(`Added ${stock.symbol} to watchlist`),
      onError: (err) =>
        toast.error("Couldn't add", {
          description: err instanceof ApiError ? err.message : "Please try again.",
        }),
    });
  }

  return (
    <section className="space-y-4">
      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search stocks by symbol or company…"
          className="pl-9"
        />
        {isFetching && (
          <Loader2 className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
        )}
      </div>

      {debounced.length > 0 && results.length === 0 && !isFetching && (
        <p className="text-sm text-muted-foreground">No matches for “{debounced}”.</p>
      )}

      <ul className="space-y-2">
        {results.map((stock) => {
          const watched = watchedIds.has(stock.id);
          const adding = add.isPending && add.variables === stock.id;
          return (
            <li
              key={stock.id}
              className="flex items-center justify-between gap-4 rounded-lg border border-border/60 bg-card/40 px-4 py-3"
            >
              <Link
                to={`/stocks/${toYahooTicker(stock.symbol, stock.exchange)}`}
                state={{ name: stock.company_name }}
                className="min-w-0 flex-1 rounded-md transition-colors hover:opacity-80"
              >
                <div className="flex items-center gap-2">
                  <span className="font-medium">{stock.symbol}</span>
                  <Badge variant="secondary">{stock.exchange}</Badge>
                </div>
                <p className="truncate text-sm text-muted-foreground">{stock.company_name}</p>
              </Link>
              <Button
                size="sm"
                variant={watched ? "secondary" : "default"}
                disabled={watched || adding}
                onClick={() => handleAdd(stock)}
              >
                {watched ? (
                  <>
                    <Check className="mr-1.5 h-4 w-4" /> Added
                  </>
                ) : adding ? (
                  <>
                    <Loader2 className="mr-1.5 h-4 w-4 animate-spin" /> Adding
                  </>
                ) : (
                  <>
                    <Plus className="mr-1.5 h-4 w-4" /> Add
                  </>
                )}
              </Button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
