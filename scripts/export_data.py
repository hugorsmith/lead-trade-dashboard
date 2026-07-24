#!/usr/bin/env python
"""Export the trade dataset into compact static assets the browser loads directly.

The dashboard has no backend: the browser fetches these two files once and does
all filtering, aggregation and charting in JavaScript. This script is the only
Python left in the request path, and it runs at build time, not at request time.

Outputs (into ``frontend/public/data/``):

    trade.tsv   One row per trade flow, tab-separated, with a header:
                    year  exporter  importer  product  value  quantity
                Countries are ISO-3 codes and products are 6-digit HS codes;
                both are resolved to display names in the browser via meta.json.
                An empty ``quantity`` means "not reported" and sums as 0, which
                is what pandas' ``groupby().sum()`` did on the server.

    meta.json   Everything the filters and legends need: the year range, the
                country geo hierarchy (region > subregion > intermediate >
                country), and the HS product metadata (categories, colours,
                labels, definitions).

Deliberately NOT written as ``.csv``: ``*.csv`` is git-LFS-tracked in this repo,
and static hosts (Cloudflare Pages, Vercel) serve the LFS *pointer file* rather
than its contents, which would silently ship a 130-byte stub to the browser.

Run:  ./venv/bin/python scripts/export_data.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

# Allow "python scripts/export_data.py" from the repo root (put root on path).
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import (  # noqa: E402
    HS_CODE_CATEGORIES,
    HS_CODE_LABELS,
    HS_CODE_COLORS,
    CATEGORY_COLORS,
    PRODUCT_DEFINITIONS,
)
from src.data_loader import load_trade_data, load_country_data  # noqa: E402

OUT = ROOT / "frontend" / "public" / "data"

# The columns the browser actually needs. Everything else in the source CSV
# (numeric country codes, country names, product descriptions) is either
# redundant with these or reconstructable from meta.json.
COLUMNS = ["year", "exporter", "importer", "product", "value", "quantity"]


def build_trade_tsv(df: pd.DataFrame) -> pd.DataFrame:
    """Reduce the source frame to the six columns shipped to the browser."""
    out = pd.DataFrame(
        {
            "year": df["year"].astype(int),
            "exporter": df["exporter_iso3"],
            "importer": df["importer_iso3"],
            "product": df["product"],
            "value": df["value"],
            "quantity": df["quantity"],
        }
    )
    return out[COLUMNS]


def build_meta(trade: pd.DataFrame, countries: pd.DataFrame) -> dict:
    """Filter options, geo hierarchy and product metadata (mirrors /api/meta)."""
    geo_cols = ["region", "subregion", "intermediate_region", "name", "iso_3"]
    present = [c for c in geo_cols if c in countries.columns]

    # NaN -> None per cell: all-null columns like intermediate_region are float
    # dtype, so a blanket .where(..., None) would leave NaN and break JSON.
    hierarchy = [
        {k: (None if pd.isna(v) else v) for k, v in row.items()}
        for row in countries[present].to_dict(orient="records")
    ]
    # Only countries that actually appear in the trade data are selectable.
    present_iso = set(trade["exporter"]) | set(trade["importer"])
    hierarchy = [r for r in hierarchy if r.get("iso_3") in present_iso]

    regions = sorted(countries["region"].dropna().drop_duplicates().tolist())

    categories = [
        {
            "category": category,
            "base_color": CATEGORY_COLORS[category]["base"],
            "products": [
                {
                    "hs_code": code,
                    "name": name,
                    "label": HS_CODE_LABELS[code],
                    "color": HS_CODE_COLORS[code],
                    "definition": PRODUCT_DEFINITIONS[code],
                }
                for code, name in products
            ],
        }
        for category, products in HS_CODE_CATEGORIES.items()
    ]

    return {
        "year_min": int(trade["year"].min()),
        "year_max": int(trade["year"].max()),
        "regions": regions,
        "hierarchy": hierarchy,
        "categories": categories,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    trade_raw = load_trade_data(str(ROOT / "lead_trade_data.csv"))
    countries = load_country_data(str(ROOT / "countries.csv"))

    trade = build_trade_tsv(trade_raw)
    tsv_path = OUT / "trade.tsv"
    # na_rep='' keeps unreported quantities as empty cells (parsed as 0).
    trade.to_csv(tsv_path, sep="\t", index=False, na_rep="")

    meta = build_meta(trade, countries)
    meta_path = OUT / "meta.json"
    meta_path.write_text(
        json.dumps(meta, separators=(",", ":"), ensure_ascii=False),
        encoding="utf-8",
    )

    tsv_mb = tsv_path.stat().st_size / 1e6
    meta_kb = meta_path.stat().st_size / 1e3
    print(f"  {tsv_path.relative_to(ROOT)}  {len(trade):,} rows  {tsv_mb:.1f} MB")
    print(f"  {meta_path.relative_to(ROOT)}  {len(meta['hierarchy'])} countries  {meta_kb:.0f} KB")


if __name__ == "__main__":
    main()
