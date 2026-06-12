"""Build lead_trade_data.csv from a raw CEPII BACI release.

Filters BACI bilateral trade flows to the 8 lead-related HS92 codes used by
the dashboard, joins country and product reference tables, and writes the
flat CSV that src/data_loader.py expects.

Usage:
    python scripts/build_lead_trade_data.py \\
        --baci-dir data/raw/BACI_HS92_V202601 \\
        --out lead_trade_data.csv \\
        --start-year 2012 --end-year 2024

    python scripts/build_lead_trade_data.py \\
        --baci-dir data/raw/BACI_HS92_V202601 --dry-run

Hybrid mode (preserve HS codes the new release dropped, by reading them from
the previous build):

    python scripts/build_lead_trade_data.py \\
        --baci-dir data/raw/BACI_HS92_V202601 \\
        --legacy-csv lead_trade_data.csv.bak \\
        --legacy-only-codes 854810
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from pathlib import Path

import pandas as pd

# Allow running from repo root: `python scripts/build_lead_trade_data.py ...`
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.config import HS_CODE_CATEGORIES  # noqa: E402

LEAD_HS_CODES = {
    code for products in HS_CODE_CATEGORIES.values() for code, _ in products
}

OUTPUT_COLUMNS = [
    "year", "exporter", "importer", "product", "value", "quantity",
    "exporter_name", "exporter_iso3", "importer_name", "importer_iso3",
    "product_description",
]


def find_one(baci_dir: Path, pattern: str) -> Path:
    matches = sorted(baci_dir.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No file matching {pattern!r} in {baci_dir}")
    if len(matches) > 1:
        raise RuntimeError(f"Ambiguous match for {pattern!r}: {matches}")
    return matches[0]


def load_year_file(path: Path, hs_filter: set[str]) -> pd.DataFrame:
    """Read a BACI yearfile, filter to the given HS codes, normalize columns."""
    df = pd.read_csv(
        path,
        dtype={"t": "int32", "i": "int32", "j": "int32", "k": "string", "v": "float64", "q": "string"},
        na_values=["NA", "           NA"],
    )
    df["k"] = df["k"].str.strip().str.zfill(6)
    df = df[df["k"].isin(hs_filter)].copy()
    df["q"] = pd.to_numeric(df["q"].str.strip(), errors="coerce")
    df = df.rename(columns={
        "t": "year", "i": "exporter", "j": "importer",
        "k": "product", "v": "value", "q": "quantity",
    })
    return df


def _fix_double_encoded(s: str) -> str:
    """Repair double-encoded UTF-8 mojibake (e.g. 'TÃ¼rkiye' -> 'Türkiye').

    BACI's country_codes file is UTF-8 but the country names inside it were
    originally UTF-8 bytes decoded as latin-1 and re-encoded as UTF-8. The
    inverse — encode as latin-1, decode as UTF-8 — recovers the original.
    Strings that don't round-trip cleanly are passed through unchanged.
    """
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def load_country_codes(path: Path) -> pd.DataFrame:
    """BACI country_codes columns: country_code, country_name, country_iso2, country_iso3."""
    df = pd.read_csv(path, encoding="utf-8")
    keep = {"country_code": "code", "country_name": "name", "country_iso3": "iso3"}
    missing = set(keep) - set(df.columns)
    if missing:
        raise RuntimeError(f"country_codes file missing columns: {missing}. Got: {list(df.columns)}")
    df = df[list(keep)].rename(columns=keep)
    df["name"] = df["name"].map(_fix_double_encoded)
    return df


def load_product_codes(path: Path) -> pd.DataFrame:
    """BACI product_codes columns: code, description."""
    df = pd.read_csv(path, encoding="utf-8", dtype={"code": "string"})
    if "description" not in df.columns or "code" not in df.columns:
        raise RuntimeError(f"product_codes missing code/description. Got: {list(df.columns)}")
    df["code"] = df["code"].str.strip().str.zfill(6)
    return df[["code", "description"]].rename(columns={"description": "product_description"})


def load_legacy_rows(legacy_csv: Path, codes: set[str], start_year: int, end_year: int) -> pd.DataFrame:
    """Read selected HS codes from a previously-built lead_trade_data.csv.

    Used to preserve codes the new BACI release no longer publishes (e.g. 854810
    was dropped from HS92 in V202601). Mojibake from older releases is corrected
    here so the output CSV is clean UTF-8 with no need for runtime fixups.
    """
    df = pd.read_csv(legacy_csv, encoding="utf-8", dtype={"product": "string"})
    df["product"] = df["product"].str.strip().str.zfill(6)
    df = df[df["product"].isin(codes) & df["year"].between(start_year, end_year)].copy()

    for col in ("exporter_name", "importer_name"):
        df[col] = df[col].map(_fix_double_encoded)

    missing = set(OUTPUT_COLUMNS) - set(df.columns)
    if missing:
        raise RuntimeError(f"legacy CSV missing columns: {missing}")
    return df[OUTPUT_COLUMNS]


def build(baci_dir: Path, start_year: int, end_year: int,
          legacy_csv: Path | None = None, legacy_only_codes: set[str] | None = None) -> pd.DataFrame:
    legacy_only_codes = legacy_only_codes or set()
    hs_filter = LEAD_HS_CODES - legacy_only_codes

    country_codes_path = find_one(baci_dir, "country_codes_V*.csv")
    product_codes_path = find_one(baci_dir, "product_codes_HS92_V*.csv")
    countries = load_country_codes(country_codes_path)
    products = load_product_codes(product_codes_path)

    year_files = sorted(baci_dir.glob("BACI_HS92_Y*_V*.csv"))
    if not year_files:
        raise FileNotFoundError(f"No BACI_HS92_Y*_V*.csv files in {baci_dir}")

    frames: list[pd.DataFrame] = []
    for yf in year_files:
        # Filename pattern: BACI_HS92_Y{YYYY}_V{VVVVVV}.csv
        try:
            year = int(yf.name.split("_Y", 1)[1].split("_", 1)[0])
        except (IndexError, ValueError):
            print(f"  skipping unparseable filename: {yf.name}", file=sys.stderr)
            continue
        if not (start_year <= year <= end_year):
            continue
        print(f"  reading {yf.name} ...", file=sys.stderr)
        frames.append(load_year_file(yf, hs_filter))

    if not frames:
        raise RuntimeError(f"No yearfiles in range {start_year}-{end_year} found")

    df = pd.concat(frames, ignore_index=True)

    df = df.merge(
        countries.rename(columns={"code": "exporter", "name": "exporter_name", "iso3": "exporter_iso3"}),
        on="exporter", how="left",
    )
    df = df.merge(
        countries.rename(columns={"code": "importer", "name": "importer_name", "iso3": "importer_iso3"}),
        on="importer", how="left",
    )
    df = df.merge(products.rename(columns={"code": "product"}), on="product", how="left")

    unmatched_exporter = df["exporter_name"].isna().sum()
    unmatched_importer = df["importer_name"].isna().sum()
    unmatched_product = df["product_description"].isna().sum()
    if unmatched_exporter or unmatched_importer:
        bad_codes = sorted(set(df.loc[df["exporter_name"].isna(), "exporter"].tolist()
                               + df.loc[df["importer_name"].isna(), "importer"].tolist()))
        raise RuntimeError(
            f"Unmapped country codes in BACI data: {bad_codes}. "
            f"({unmatched_exporter} exporter rows, {unmatched_importer} importer rows)"
        )
    if unmatched_product:
        bad = sorted(df.loc[df["product_description"].isna(), "product"].unique())
        raise RuntimeError(f"Unmapped product codes: {bad}")

    df = df[OUTPUT_COLUMNS]

    if legacy_csv and legacy_only_codes:
        print(f"  appending {sorted(legacy_only_codes)} from {legacy_csv} ...", file=sys.stderr)
        legacy = load_legacy_rows(legacy_csv, legacy_only_codes, start_year, end_year)
        if legacy.empty:
            raise RuntimeError(f"Legacy CSV had no rows for codes {sorted(legacy_only_codes)} in {start_year}-{end_year}")
        df = pd.concat([df, legacy], ignore_index=True)

    df = df.sort_values(["year", "exporter", "importer", "product"]).reset_index(drop=True)
    return df


def summarize(df: pd.DataFrame) -> None:
    print("\n=== Summary ===")
    print(f"Total rows: {len(df):,}")
    print(f"Years: {df['year'].min()}–{df['year'].max()}")
    print("\nRows per year:")
    print(df.groupby("year").size().to_string())
    print(f"\nUnique exporters: {df['exporter'].nunique()}")
    print(f"Unique importers: {df['importer'].nunique()}")
    print(f"Unique HS codes: {df['product'].nunique()} (expected {len(LEAD_HS_CODES)})")
    print(f"Null quantities: {df['quantity'].isna().sum()} (BACI reports value but not weight for some flows)")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--baci-dir", required=True, type=Path,
                   help="Directory containing the unzipped BACI HS92 release.")
    p.add_argument("--out", type=Path, default=Path("lead_trade_data.csv"),
                   help="Output CSV path (default: lead_trade_data.csv).")
    p.add_argument("--start-year", type=int, default=2012)
    p.add_argument("--end-year", type=int, default=2024)
    p.add_argument("--legacy-csv", type=Path, default=None,
                   help="Optional path to a previously-built lead_trade_data.csv. Used together with "
                        "--legacy-only-codes to preserve HS codes the new BACI release no longer publishes.")
    p.add_argument("--legacy-only-codes", nargs="*", default=[],
                   help="HS codes to read from --legacy-csv instead of the new BACI release.")
    p.add_argument("--dry-run", action="store_true",
                   help="Build the dataset and print a summary but do not write the output file.")
    args = p.parse_args()

    if not args.baci_dir.is_dir():
        print(f"error: --baci-dir {args.baci_dir} is not a directory", file=sys.stderr)
        return 2

    legacy_codes = {c.zfill(6) for c in args.legacy_only_codes}
    if legacy_codes and not args.legacy_csv:
        print("error: --legacy-only-codes requires --legacy-csv", file=sys.stderr)
        return 2
    if args.legacy_csv and not args.legacy_csv.is_file():
        print(f"error: --legacy-csv {args.legacy_csv} not found", file=sys.stderr)
        return 2

    df = build(args.baci_dir, args.start_year, args.end_year,
               legacy_csv=args.legacy_csv, legacy_only_codes=legacy_codes)
    summarize(df)

    if args.dry_run:
        print("\n[dry run] not writing output.")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False, encoding="utf-8")
    size_mb = os.path.getsize(args.out) / (1024 * 1024)
    print(f"\nWrote {args.out} ({size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
