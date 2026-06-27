import { useMemo } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { PredictionPoint, PricePoint } from "@/lib/ml";

type Row = { date: string; actual: number | null; forecast: number | null };

function addOneDay(isoDate: string): string {
  const d = new Date(isoDate);
  d.setDate(d.getDate() + 1);
  return d.toISOString().slice(0, 10);
}

/** Combined chart: recent actual closes plus the model's forward forecast. */
export function PriceChart({
  history,
  forecast,
  historyDays = 90,
}: {
  history: PricePoint[];
  forecast: PredictionPoint[];
  historyDays?: number;
}) {
  const data = useMemo<Row[]>(() => {
    const recent = history.slice(-historyDays);
    const rows: Row[] = recent.map((p) => ({ date: p.date, actual: p.close, forecast: null }));

    if (recent.length > 0 && forecast.length > 0) {
      // anchor the forecast line to the last actual point so they connect
      rows[rows.length - 1].forecast = recent[recent.length - 1].close;
      let date = recent[recent.length - 1].date;
      for (const f of forecast) {
        date = addOneDay(date);
        rows.push({ date, actual: null, forecast: f.predicted_close });
      }
    }
    return rows;
  }, [history, forecast, historyDays]);

  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data} margin={{ top: 8, right: 12, bottom: 8, left: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border) / 0.3)" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
          minTickGap={32}
        />
        <YAxis
          domain={["auto", "auto"]}
          tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
          width={56}
          tickFormatter={(v: number) => v.toFixed(0)}
        />
        <Tooltip
          contentStyle={{
            background: "hsl(var(--popover))",
            border: "1px solid hsl(var(--border))",
            borderRadius: 8,
            fontSize: 12,
          }}
          labelStyle={{ color: "hsl(var(--muted-foreground))" }}
          formatter={(value) => (typeof value === "number" ? value.toFixed(2) : String(value))}
        />
        <Line
          type="monotone"
          dataKey="actual"
          name="Actual"
          stroke="hsl(var(--primary))"
          strokeWidth={2}
          dot={false}
          connectNulls
        />
        <Line
          type="monotone"
          dataKey="forecast"
          name="Forecast"
          stroke="hsl(var(--primary))"
          strokeWidth={2}
          strokeDasharray="5 4"
          dot={false}
          connectNulls
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
