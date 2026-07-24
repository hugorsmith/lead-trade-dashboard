# Lead Trade Dashboard

An interactive dashboard for analyzing global lead trade data from 2012–2024.

## Overview

This dashboard provides visualization and analysis of international lead trade flows, including:

- Lead ores and concentrates
- Refined and unwrought lead
- New lead-acid batteries (SLI and other)
- Used batteries and lead scrap

It is a **static React app with no backend**. The browser downloads the trade
dataset once (~2 MB gzipped) and computes every KPI, aggregation and chart
locally, so the whole thing can be served from any static host.

## Features

- **Geographic Filtering**: Filter by region, sub-region, intermediate region, or specific country
- **Product Selection**: Choose specific HS codes or product categories to analyze
- **Time Range Selection**: Adjust the year range for analysis (2012–2024)
- **Interactive Visualizations**:
  - Choropleth map showing net trade partners
  - Stacked bar charts for exports/imports by category
  - Top trading partner rankings
  - "Safety of source" view for US refined-lead imports
- **Data Export**: Download filtered data as CSV (generated in the browser)
- **Shareable links**: `?country=NGA` (ISO-3) selects a country on load

## Data Sources

- **Trade Data**: [CEPII BACI](http://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37) dataset - Harmonized bilateral trade flows
- **Country Metadata**: UN M49 regional classifications
- **Product Codes**: [Harmonized System (HS)](https://www.wcotradetools.org/en/harmonized-system) 6-digit codes

## Architecture

```
lead_trade_data.csv  (34 MB, Git LFS)
        │
        │  scripts/export_data.py      (build-time, run when the data changes)
        ▼
frontend/public/data/
   trade.tsv   192,908 rows — year, exporter, importer, product, value, quantity
   meta.json   year range, country geo hierarchy, HS product metadata
        │
        │  fetched once by the browser
        ▼
frontend/src/data/   filtering, aggregation and Plotly figure building, in JS
```

`trade.tsv` is deliberately **not** a `.csv`: `*.csv` is Git-LFS-tracked here, and
static hosts serve the LFS *pointer file* rather than its contents.

## Setup

### Run the dashboard

```bash
npm --prefix frontend install
npm --prefix frontend run dev      # http://localhost:5173
```

Build a deployable static site into `frontend/dist/`:

```bash
npm --prefix frontend run build
npm --prefix frontend run preview  # serve the build locally
```

`frontend/dist/` is self-contained — deploy it to any static host.

### Regenerate the browser data

Only needed after the underlying dataset changes:

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python scripts/export_data.py
```

## Development

```bash
pip install -r requirements-dev.txt
pytest tests/ -o addopts=""   # pytest.ini's --cov flags need pytest-cov
```

## Project Structure

```
lead-trade-dashboard/
├── frontend/
│   ├── public/data/       # trade.tsv + meta.json (generated, committed)
│   └── src/
│       ├── App.jsx        # layout, routing, filter state
│       ├── api.js         # local "endpoints" + geo cascade
│       ├── components/    # filters, KPI row, tabs, charts, safety view
│       └── data/          # store, aggregations, figures, theming, config
├── src/                   # Python: config + data loading (used by scripts/)
├── scripts/
│   ├── build_lead_trade_data.py  # builds lead_trade_data.csv from BACI
│   └── export_data.py            # builds the browser data assets
├── tests/                 # Python test suite
├── lead_trade_data.csv    # Trade data (Git LFS)
└── countries.csv          # Country metadata (Git LFS)
```

## Deployment

The build output is a plain static directory, so any static host works
(Cloudflare Pages, Netlify, GitHub Pages, S3, nginx):

- **Build command**: `npm --prefix frontend ci && npm --prefix frontend run build`
- **Output directory**: `frontend/dist`

Because the app is a single-page app, configure the host to rewrite unknown
paths to `/index.html`.

## License

MIT
