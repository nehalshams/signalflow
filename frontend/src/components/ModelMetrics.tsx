import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Loader2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { getTrainingRuns } from "@/lib/ml";
import type { TrainingRun, TrainingRunStatus } from "@/lib/ml";

const STATUS_LABEL: Record<TrainingRunStatus, string> = {
  success: "Healthy",
  degraded: "Drift",
  failed: "Failed",
};

function statusVariant(status: TrainingRunStatus): "secondary" | "destructive" | "outline" {
  if (status === "failed") return "destructive";
  if (status === "degraded") return "outline";
  return "secondary";
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.round(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.round(hrs / 24)}d ago`;
}

const fmt = (v: number | null, suffix = "") => (v === null ? "—" : `${v}${suffix}`);

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border/60 bg-card/40 px-3 py-2">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="font-display text-lg font-semibold tabular-nums">{value}</div>
    </div>
  );
}

export function ModelMetrics({ ticker }: { ticker: string }) {
  const { data: runs = [], isLoading } = useQuery<TrainingRun[]>({
    queryKey: ["trainingRuns", ticker],
    queryFn: () => getTrainingRuns(ticker),
    enabled: ticker.length > 0,
  });

  if (isLoading) {
    return (
      <p className="flex items-center gap-2 text-sm text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" /> Loading model history…
      </p>
    );
  }

  if (runs.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No training runs recorded yet. Train the model to see its accuracy here.
      </p>
    );
  }

  const latest = runs[0];

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <Badge variant={statusVariant(latest.status)}>{STATUS_LABEL[latest.status]}</Badge>
        <span className="text-sm text-muted-foreground">
          Last trained {timeAgo(latest.created_at)}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Metric label="MAPE" value={fmt(latest.mape, "%")} />
        <Metric label="RMSE" value={fmt(latest.rmse)} />
        <Metric label="MAE" value={fmt(latest.mae)} />
        <Metric label="Epochs" value={fmt(latest.epochs_run)} />
      </div>

      {latest.status === "degraded" && latest.notes && (
        <p className="flex items-start gap-2 rounded-lg border border-border/60 bg-card/40 px-3 py-2 text-sm text-muted-foreground">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-500" />
          {latest.notes}
        </p>
      )}

      {runs.length > 1 && (
        <div>
          <h3 className="mb-2 text-sm font-medium text-muted-foreground">Training history</h3>
          <ul className="divide-y divide-border/60 rounded-lg border border-border/60">
            {runs.map((run) => (
              <li key={run.id} className="flex items-center justify-between gap-4 px-3 py-2 text-sm">
                <span className="text-muted-foreground">{timeAgo(run.created_at)}</span>
                <span className="flex items-center gap-3">
                  <span className="tabular-nums">MAPE {fmt(run.mape, "%")}</span>
                  <Badge variant={statusVariant(run.status)}>{STATUS_LABEL[run.status]}</Badge>
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
