# Lead Trade Dashboard

An interactive Streamlit dashboard for analyzing global lead trade data from 2012-2024.

## Overview

This dashboard provides visualization and analysis of international lead trade flows, including:

- Lead ores and concentrates
- Refined and unwrought lead
- New lead-acid batteries (SLI and other)
- Used batteries and lead scrap

## Features

- **Geographic Filtering**: Filter by region, sub-region, intermediate region, or specific country
- **Product Selection**: Choose specific HS codes or product categories to analyze
- **Time Range Selection**: Adjust the year range for analysis (2012-2024)
- **Interactive Visualizations**:
  - Choropleth map showing net trade partners
  - Stacked bar charts for exports/imports by category
  - Top trading partner rankings
- **Data Export**: Download filtered data as CSV

## Data Sources

- **Trade Data**: [CEPII BACI](http://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37) dataset - Harmonized bilateral trade flows
- **Country Metadata**: UN M49 regional classifications
- **Product Codes**: [Harmonized System (HS)](https://www.wcotradetools.org/en/harmonized-system) 6-digit codes

## Setup

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hugorsmith/lead-trade-dashboard.git
   cd lead-trade-dashboard
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the dashboard:
   ```bash
   streamlit run app.py
   ```

The dashboard will open in your browser at `http://localhost:8501`.

## Development

### Install dev dependencies

```bash
pip install -r requirements-dev.txt
```

### Run tests

```bash
pytest tests/
```

## Project Structure

```
lead-trade-dashboard/
├── app.py                 # Main Streamlit application
├── src/
│   ├── config.py          # Product definitions, HS codes, color schemes
│   ├── data_loader.py     # Data loading and processing functions
│   ├── filters.py         # Geographic filter functions
│   ├── calculations.py    # Trade metric calculations
│   └── charts.py          # Plotly chart styling functions
├── tests/                 # Test suite
├── lead_trade_data.csv    # Trade data (Git LFS)
├── countries.csv          # Country metadata
└── requirements.txt       # Python dependencies
```

## Deployment

The dashboard is automatically deployed to a Hetzner VPS via GitHub Actions on push to `main`. The workflow:

1. SSHs into the VPS
2. Pulls the latest code (including Git LFS files)
3. Updates dependencies
4. Restarts the Streamlit service

## License

MIT
