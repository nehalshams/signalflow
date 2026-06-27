import { Link } from "react-router-dom";
import { Loader2, Star, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ApiError } from "@/lib/api";
import { toYahooTicker } from "@/lib/stocks";
import { useRemoveFromWatchlist, useWatchlist } from "@/hooks/useWatchlist";

export function Watchlist() {
  const { data: items = [], isLoading, isError } = useWatchlist();
  const remove = useRemoveFromWatchlist();

  function handleRemove(stockId: number, symbol: string) {
    remove.mutate(stockId, {
      onSuccess: () => toast.success(`Removed ${symbol}`),
      onError: (err) =>
        toast.error("Couldn't remove", {
          description: err instanceof ApiError ? err.message : "Please try again.",
        }),
    });
  }

  if (isLoading) {
    return (
      <p className="flex items-center gap-2 text-sm text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" /> Loading watchlist…
      </p>
    );
  }

  if (isError) {
    return <p className="text-sm text-destructive">Couldn't load your watchlist.</p>;
  }

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 rounded-lg border border-dashed border-border/60 py-10 text-center">
        <Star className="h-6 w-6 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">
          Your watchlist is empty. Search above to add stocks.
        </p>
      </div>
    );
  }

  return (
    <ul className="space-y-2">
      {items.map((item) => {
        const removing = remove.isPending && remove.variables === item.stock.id;
        return (
          <li
            key={item.id}
            className="flex items-center justify-between gap-4 rounded-lg border border-border/60 bg-card/40 px-4 py-3"
          >
            <Link
              to={`/stocks/${toYahooTicker(item.stock.symbol, item.stock.exchange)}`}
              state={{ name: item.stock.company_name }}
              className="min-w-0 flex-1 rounded-md transition-colors hover:opacity-80"
            >
              <div className="flex items-center gap-2">
                <span className="font-medium">{item.stock.symbol}</span>
                <Badge variant="secondary">{item.stock.exchange}</Badge>
              </div>
              <p className="truncate text-sm text-muted-foreground">{item.stock.company_name}</p>
            </Link>
            <Button
              size="sm"
              variant="ghost"
              disabled={removing}
              onClick={() => handleRemove(item.stock.id, item.stock.symbol)}
              aria-label={`Remove ${item.stock.symbol}`}
            >
              {removing ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Trash2 className="h-4 w-4" />
              )}
            </Button>
          </li>
        );
      })}
    </ul>
  );
}
