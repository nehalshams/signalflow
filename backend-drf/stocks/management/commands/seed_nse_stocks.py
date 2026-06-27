"""Seed the Stock table with the full list of NSE-listed equities.

Usage:
    python manage.py seed_nse_stocks            # fetch live from NSE
    python manage.py seed_nse_stocks --file EQUITY_L.csv   # load a local copy

Source: NSE's official equity list (SYMBOL, NAME OF COMPANY, SERIES, ...).
Only rows in the 'EQ' series are loaded (regular equities).
"""
import csv
import io

import requests
from django.core.management.base import BaseCommand, CommandError

from stocks.models import Stock

NSE_EQUITY_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120 Safari/537.36"
    )
}


class Command(BaseCommand):
    help = "Load the full NSE equity universe into the Stock table."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            help="Path to a local EQUITY_L.csv instead of fetching from NSE.",
        )

    def handle(self, *args, **options):
        text = self._read_csv(options.get("file"))
        rows = list(csv.DictReader(io.StringIO(text)))
        if not rows:
            raise CommandError("No rows found in the equity list.")

        existing = {s.symbol: s for s in Stock.objects.all()}
        to_create, to_update = [], []
        seen = 0

        for raw in rows:
            row = {k.strip(): (v or "").strip() for k, v in raw.items()}
            if row.get("SERIES") != "EQ":
                continue
            symbol = row["SYMBOL"].upper()
            name = row["NAME OF COMPANY"]
            if not symbol or not name:
                continue
            seen += 1

            current = existing.get(symbol)
            if current is None:
                to_create.append(
                    Stock(symbol=symbol, company_name=name, exchange="NSE", is_active=True)
                )
            elif current.company_name != name or not current.is_active:
                current.company_name = name
                current.is_active = True
                to_update.append(current)

        Stock.objects.bulk_create(to_create, batch_size=500, ignore_conflicts=True)
        Stock.objects.bulk_update(to_update, ["company_name", "is_active"], batch_size=500)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done — {seen} EQ rows processed: "
                f"{len(to_create)} created, {len(to_update)} updated, "
                f"{Stock.objects.count()} total stocks."
            )
        )

    def _read_csv(self, path):
        if path:
            self.stdout.write(f"Reading equities from {path} ...")
            try:
                with open(path, encoding="utf-8") as f:
                    return f.read()
            except OSError as e:
                raise CommandError(f"Could not read {path}: {e}")

        self.stdout.write(f"Fetching equities from {NSE_EQUITY_URL} ...")
        try:
            resp = requests.get(NSE_EQUITY_URL, headers=_HEADERS, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise CommandError(
                f"Failed to fetch NSE list ({e}). "
                f"Download it manually and pass --file EQUITY_L.csv."
            )
        return resp.text
