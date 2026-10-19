"""Download day-ahead prices, generation by type and load from ENTSO-E.

Usage:
    export ENTSOE_API_KEY="your-token"
    python src/download_entsoe.py --countries ES --start 2023-01-01 --end 2025-12-31

Notes:
- Token: create an account on transparency.entsoe.eu, then request API access
  (see the platform's "RESTful API" help page).
- Data are downloaded year by year to avoid timeouts.
- Check the time resolution of each series (hourly vs 15 min) before comparing countries.
"""
import argparse
import os
from pathlib import Path

import pandas as pd
from entsoe import EntsoePandasClient

# Bidding zones used by ENTSO-E (Germany is DE_LU, Italy North is IT_NORD, etc.)
ZONES = {"ES": "ES", "FR": "FR", "DE": "DE_LU", "NL": "NL"}
OUT = Path("data/raw")


def year_ranges(start: str, end: str, tz: str = "Europe/Brussels"):
    s, e = pd.Timestamp(start, tz=tz), pd.Timestamp(end, tz=tz)
    cur = s
    while cur < e:
        nxt = min(pd.Timestamp(year=cur.year + 1, month=1, day=1, tz=tz), e + pd.Timedelta(days=1))
        yield cur, nxt
        cur = nxt


def fetch(client, zone_name, zone, start, end):
    OUT.mkdir(parents=True, exist_ok=True)
    prices, gen, load, load_fc, ws_fc = [], [], [], [], []
    for a, b in year_ranges(start, end):
        print(f"{zone_name}: {a.date()} -> {b.date()}")
        prices.append(client.query_day_ahead_prices(zone, start=a, end=b))
        gen.append(client.query_generation(zone, start=a, end=b, psr_type=None))
        load.append(client.query_load(zone, start=a, end=b))
        # Day-ahead forecasts (known before the auction): use these as features for forecasting
        load_fc.append(client.query_load_forecast(zone, start=a, end=b))
        ws_fc.append(client.query_wind_and_solar_forecast(zone, start=a, end=b, psr_type=None))
    pd.concat(prices).rename("price_eur_mwh").to_csv(OUT / f"{zone_name}_prices.csv")
    pd.concat(gen).to_csv(OUT / f"{zone_name}_generation.csv")
    pd.concat(load).to_csv(OUT / f"{zone_name}_load.csv")
    pd.concat(load_fc).to_csv(OUT / f"{zone_name}_load_forecast.csv")
    pd.concat(ws_fc).to_csv(OUT / f"{zone_name}_wind_solar_forecast.csv")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--countries", nargs="+", default=["ES"])
    p.add_argument("--start", default="2023-01-01")
    p.add_argument("--end", default="2025-12-31")
    args = p.parse_args()

    key = os.environ.get("ENTSOE_API_KEY")
    if not key:
        raise SystemExit("Set ENTSOE_API_KEY first.")
    client = EntsoePandasClient(api_key=key)
    for c in args.countries:
        fetch(client, c, ZONES[c], args.start, args.end)


if __name__ == "__main__":
    main()
