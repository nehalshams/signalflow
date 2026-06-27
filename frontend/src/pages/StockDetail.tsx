import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Brain, Loader2, TrendingUp } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ApiError } from "@/lib/api";
import { getPrediction, getPriceHistory, getTrainStatus, trainModel } from "@/lib/ml";
import { PriceChart } from "@/components/PriceChart";
import { ModelMetrics } from "@/components/ModelMetrics";

const TERMINAL = ["SUCCESS", "FAILURE"];

const StockDetail = () => {
  const { ticker = "" } = useParams();
  const location = useLocation();
  const displayName = (location.state as { name?: string } | null)?.name;
  const queryClient = useQueryClient();

  const history = useQuery({
    queryKey: ["history", ticker],
    queryFn: () => getPriceHistory(ticker, 1),
    enabled: ticker.length > 0,
  });

  const prediction = useQuery({
    queryKey: ["prediction", ticker],
    queryFn: () => getPrediction(ticker, 30),
    enabled: ticker.length > 0,
    retry: false, // a 404 (untrained) shouldn't be retried
  });

  // ── training flow ──────────────────────────────────────────────
  const [taskId, setTaskId] = useState<string | null>(null);

  const train = useMutation({
    mutationFn: () => trainModel(ticker),
    onSuccess: (res) => {
      setTaskId(res.task_id);
      toast.info("Training queued", { description: "This can take a minute…" });
    },
    onError: (err) =>
      toast.error("Couldn't start training", {
        description: err instanceof ApiError ? err.message : "Please try again.",
      }),
  });

  const status = useQuery({
    queryKey: ["trainStatus", taskId],
    queryFn: () => getTrainStatus(taskId as string),
    enabled: taskId !== null,
    refetchInterval: (q) => (TERMINAL.includes(q.state.data?.state ?? "") ? false : 2000),
  });

  useEffect(() => {
    const state = status.data?.state;
    if (!state || !TERMINAL.includes(state)) return;
    if (state === "SUCCESS") {
      toast.success("Model trained");
      queryClient.invalidateQueries({ queryKey: ["prediction", ticker] });
      queryClient.invalidateQueries({ queryKey: ["trainingRuns", ticker] });
    } else {
      toast.error("Training failed", { description: status.data?.error });
    }
    setTaskId(null);
  }, [status.data?.state, queryClient, ticker, status.data?.error]);

  const isTraining = train.isPending || taskId !== null;
  const notTrained = prediction.error instanceof ApiError && prediction.error.status === 404;

  return (
    <main className="relative min-h-screen overflow-hidden bg-background text-foreground">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,hsl(var(--primary)/0.15),transparent_60%)]" />

      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-4xl flex-col px-6 py-8">
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to dashboard
        </Link>

        <header className="mt-6 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary/15 shadow-glow">
            <TrendingUp className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-bold tracking-tight">{ticker}</h1>
            {displayName && <p className="text-sm text-muted-foreground">{displayName}</p>}
          </div>
        </header>

        <Card className="mt-8 border-border/60 bg-card/60 p-6 backdrop-blur-xl">
          <div className="mb-4 flex items-center justify-between gap-4">
            <h2 className="font-display text-lg font-semibold">Price & 30-day forecast</h2>
            {prediction.data && (
              <Badge variant="secondary">
                {prediction.data.cached ? "Cached forecast" : "Fresh forecast"}
              </Badge>
            )}
          </div>

          {history.isLoading ? (
            <p className="flex items-center gap-2 py-16 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" /> Loading price history…
            </p>
          ) : history.isError ? (
            <p className="py-16 text-sm text-destructive">
              {history.error instanceof ApiError
                ? history.error.message
                : "Couldn't load price history."}
            </p>
          ) : (
            <PriceChart
              history={history.data?.data ?? []}
              forecast={prediction.data?.predictions ?? []}
            />
          )}
        </Card>

        <Card className="mt-6 border-border/60 bg-card/60 p-6 backdrop-blur-xl">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="font-display text-lg font-semibold">AI model</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                {prediction.isLoading
                  ? "Loading forecast…"
                  : notTrained
                    ? "No model has been trained for this ticker yet."
                    : prediction.data
                      ? `Forecast ready — ${prediction.data.predictions.length} days projected.`
                      : "Forecast unavailable."}
              </p>
            </div>
            <Button onClick={() => train.mutate()} disabled={isTraining}>
              {isTraining ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {status.data?.state ? `Training… (${status.data.state})` : "Training…"}
                </>
              ) : (
                <>
                  <Brain className="mr-2 h-4 w-4" />
                  {notTrained ? "Train model" : "Retrain model"}
                </>
              )}
            </Button>
          </div>

          <div className="mt-6 border-t border-border/60 pt-6">
            <ModelMetrics ticker={ticker} />
          </div>
        </Card>
      </div>
    </main>
  );
};

export default StockDetail;
