import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

# Import from our modules
from src.config import (
    PRODUCT_DEFINITIONS,
    HS_CODE_CATEGORIES,
    CATEGORY_COLORS,
    HS_CODE_COLORS,
    CATEGORY_COLOR_LIST,
    HS_TO_CATEGORY,
    HS_CODE_LABELS
)
from src.data_loader import load_trade_data, load_country_data
from src.calculations import calculate_yoy_change
from src.filters import (
    get_available_subregions,
    get_available_intermediate_regions,
    get_available_countries
)
from src.charts import get_plotly_template, apply_chart_theme, apply_subplot_theme, apply_choropleth_theme


def main():
    """Main Streamlit application."""
    # Page configuration
    st.set_page_config(
        page_title="Lead Trade Analysis",
        page_icon="📊",
        layout="wide"
    )

    # Title and description
    st.title("Global Lead Trade Analysis Dashboard")
    st.markdown("""
        <style>
        .main {
            background-color: #0A1929;
            color: #E0E0E0;
        }
        .stMetric {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
            padding: 10px;
        }
        /* Light mode - darker text */
        [data-theme="light"] .stMetric label {
            color: #2C3E50 !important;
        }
        /* Dark mode - light text */
        [data-theme="dark"] .stMetric label {
            color: #E0E0E0 !important;
        }
        /* Light mode - darker text for headers */
        [data-theme="light"] h1, [data-theme="light"] h2, [data-theme="light"] h3, [data-theme="light"] p {
            color: #2C3E50 !important;
        }
        /* Dark mode - light text for headers */
        [data-theme="dark"] h1, [data-theme="dark"] h2, [data-theme="dark"] h3, [data-theme="dark"] p {
            color: #E0E0E0 !important;
        }
        /* Fix padding on the top of main section */
        .block-container {
            padding-top: 2.5rem !important;
        }
        /* Reduce divider spacing */
        hr {
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        @media (max-width: 768px) {
            .mobile-warning {
                display: block;
                background-color: rgba(255, 193, 7, 0.1);
                border-left: 5px solid #ffc107;
                padding: 1rem;
                margin: 1rem 0;
                color: #ffc107;
            }
        }
        @media (min-width: 769px) {
            .mobile-warning {
                display: none;
            }
        }
        </style>
        <div class="mobile-warning">
            📱 This dashboard is best viewed on desktop devices for the full interactive experience.
        </div>
    """, unsafe_allow_html=True)

    # Caption and links row (close to title)
    st.markdown("""
    <div style='display: flex; align-items: center; margin-top: -10px; margin-bottom: 5px; gap: 20px; flex-wrap: wrap;'>
        <span style='color: #888; font-size: 0.85rem;'>Global lead trade data 2012-2023 · CEPII BACI dataset · Weight in tons</span>
        <a href='https://leadbatteries.substack.com/' target='_blank' style='background-color: #FF4B4B; color: white; padding: 4px 10px; border-radius: 4px; text-decoration: none; font-size: 0.8rem;'>📚 Lead Battery Notes</a>
        <a href='https://github.com/hugorsmith/lead-trade-data' style='color: #4A90E2; text-decoration: none; font-size: 0.8rem;'>🔗 Data</a>
        <a href='#product-definitions' style='color: #4A90E2; text-decoration: none; font-size: 0.8rem;'>⬇️ Product Codes</a>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Get current theme from Streamlit (used by chart styling functions)
    # Note: st.get_option("theme.base") returns None when using default theme
    def get_current_theme():
        theme_base = st.get_option("theme.base")
        # Default to light if not explicitly set to dark
        return "dark" if theme_base == "dark" else "light"

    theme = get_current_theme()

    # Load the data with Streamlit caching
    @st.cache_data
    def load_data_cached():
        """Load data with Streamlit caching."""
        try:
            with st.spinner('Loading trade data...'):
                trade_df = load_trade_data()
                country_df = load_country_data()
                return trade_df, country_df
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None, None

    df, country_df = load_data_cached()
    if df is None or country_df is None:
        st.stop()

    # Sidebar for filters
    st.sidebar.header("Filters")

    # HS code selector with categories
    st.sidebar.subheader("Select Products:")

    # Create checkboxes grouped by category
    selected_hs_codes = []
    for category, products in HS_CODE_CATEGORIES.items():
        st.sidebar.markdown(f"### {category}")
        for hs_code, description in products:
            if st.sidebar.checkbox(
                f"{hs_code} - {description}", 
                value=True,  # Changed back to True to have all selected by default
                key=f"hs_code_{hs_code}"
            ):
                selected_hs_codes.append(hs_code)

    # Ensure at least one HS code is selected
    if not selected_hs_codes:
        st.sidebar.warning("Please select at least one product")
        selected_hs_codes = [list(HS_CODE_CATEGORIES.values())[0][0][0]]  # First HS code as fallback

    # Replace the metrics year selector with a date range selector
    st.sidebar.subheader("Date Range")
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    selected_years = st.sidebar.slider(
        'Select Year Range',
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

    # Country selector

    region_col, subregion_col, intermediate_col, country_col = st.columns(4)
    with region_col:
        regions = sorted(country_df['region'].drop_duplicates().to_list())
        region = st.selectbox("Region", regions, index=None)

    with subregion_col:
        subregions = get_available_subregions(country_df, region=region)
        subregion = st.selectbox("Sub-region", subregions, index=None)

    with intermediate_col:
        intermediate = get_available_intermediate_regions(country_df, region=region, subregion=subregion)
        intermediate_region = st.selectbox("Intermediate Region", intermediate, index=None)

    with country_col:
        countries = get_available_countries(country_df, region=region, subregion=subregion, intermediate_region=intermediate_region)
        country = st.selectbox("Country", countries, index=None)

    st.divider()

    # Update the data filtering
    df_filtered = df[
        (df['product'].isin(selected_hs_codes)) & 
        (df['year'].between(selected_years[0], selected_years[1]))
    ]

    # Create trade flows for selected country
    countries = [country] if country else countries
    exports = df_filtered[df_filtered.exporter_name.isin(countries)].copy()
    imports = df_filtered[df_filtered.importer_name.isin(countries)].copy()

    selected_countries = (
        country if country is not None else
        intermediate_region if intermediate_region is not None else
        subregion if subregion is not None else
        region if region is not None else
        "All Countries"
    )

    # Add key metrics at the top
    # st.subheader("Key Metrics (tons)")

    # Add year selector for metrics
    available_years = sorted(df_filtered['year'].unique(), reverse=True)  # Sort in descending order
    selected_metrics_year = df_filtered.year.max()

    # Filter data for selected year
    exports_year = exports[exports['year'] == selected_metrics_year]
    imports_year = imports[imports['year'] == selected_metrics_year]

    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

    with metrics_col1:
        total_exports = exports_year['quantity'].sum()

        # Get previous year data
        previous_year = selected_metrics_year - 1
        exports_prev_year = exports[exports['year'] == previous_year]['quantity'].sum()
        export_change = calculate_yoy_change(total_exports, exports_prev_year)
        st.metric(
            "Total Export Volume", 
            f"{total_exports:,.0f} mt",
            f"{export_change:+.1f}% vs prev year"
        )

    with metrics_col2:
        total_imports = imports_year['quantity'].sum()

        # Get previous year data
        previous_year = selected_metrics_year - 1
        imports_prev_year = imports[imports['year'] == previous_year]['quantity'].sum()
        import_change = calculate_yoy_change(total_imports, imports_prev_year)
        st.metric(
            "Total Import Volume", 
            f"{total_imports:,.0f} mt",
            f"{import_change:+.1f}% vs prev year"
        )

    with metrics_col3:
        trade_balance = total_exports - total_imports
        st.metric("Trade Balance", f"{trade_balance:,.0f} mt")

    with metrics_col4:
        num_partners = len(set(exports_year['importer_name'].unique()) | set(imports_year['exporter_name'].unique()))
        st.metric("Trading Partners", f"{num_partners}")

    # Choropleth map showing trading partners (most recent year only)
    # st.subheader("Trading Partners Map")

    # Use most recent year in selected range
    map_year = exports['year'].max() if len(exports) > 0 else selected_years[1]
    exports_map = exports[exports['year'] == map_year]
    imports_map = imports[imports['year'] == map_year]

    # Aggregate exports by destination country
    export_by_partner = (
        exports_map.groupby(['importer_name', 'importer_iso3'])['quantity']
        .sum()
        .reset_index()
        .rename(columns={'quantity': 'exports', 'importer_name': 'partner', 'importer_iso3': 'iso3'})
    )

    # Aggregate imports by source country
    import_by_partner = (
        imports_map.groupby(['exporter_name', 'exporter_iso3'])['quantity']
        .sum()
        .reset_index()
        .rename(columns={'quantity': 'imports', 'exporter_name': 'partner', 'exporter_iso3': 'iso3'})
    )

    # Merge and calculate net trade
    trade_partners = pd.merge(
        export_by_partner,
        import_by_partner,
        on=['partner', 'iso3'],
        how='outer'
    ).fillna(0)
    trade_partners['net_trade'] = trade_partners['exports'] - trade_partners['imports']

    if len(trade_partners) > 0:
        # Create diverging color scale: purple for exports, green for imports
        max_abs = max(abs(trade_partners['net_trade'].min()), abs(trade_partners['net_trade'].max()), 1)

        fig_map = px.choropleth(
            trade_partners,
            locations='iso3',
            color='net_trade',
            hover_name='partner',
            hover_data={
                'iso3': False,
                'exports': ':,.0f',
                'imports': ':,.0f',
                'net_trade': ':,.0f'
            },
            color_continuous_scale=[
                [0, '#1b7837'],      # Dark green (net importer)
                [0.5, '#f7f7f7'],    # White/neutral
                [1, '#762a83']       # Purple (net exporter)
            ],
            range_color=[-max_abs, max_abs],
            labels={'net_trade': 'Net Trade (tons)', 'exports': 'Exports', 'imports': 'Imports'}
        )

        apply_choropleth_theme(
            fig_map,
            title=f'Net Trade Partners for {selected_countries} ({int(map_year)})',
            theme=theme,
        )

        # st.plotly_chart(fig_map, width='stretch')
    else:
        st.info("No trade partner data available for the selected filters.")

    # Create labels for the HS codes (use imported labels)
    hs_code_labels = HS_CODE_LABELS

    yearly_exports = (
        exports.groupby(['year', 'category', 'product'])['quantity']
        .sum()
        .reset_index()
        .assign(
            product_label = lambda x: x['product'].map(hs_code_labels),
            order = lambda x: x['product'].map({c: i for i, c in enumerate(HS_TO_CATEGORY.keys())})
        )
        .sort_values(['order'])
    )

    yearly_imports = (
        imports.groupby(['year', 'category', 'product'])['quantity']
        .sum()
        .reset_index()
        .assign(
            product_label = lambda x: x['product'].map(hs_code_labels),
            order = lambda x: x['product'].map({c: i for i, c in enumerate(HS_TO_CATEGORY.keys())})
        )
        .sort_values(['order'])
    )

    # Show trade imbalance
    yearly_trades = (
        pd.concat([
            yearly_imports.assign(direction = "imports"),
            yearly_exports.assign(direction = "exports")
        ])
        .groupby(['year', 'category', 'direction'])['quantity']
        .sum()
        .reset_index()
        .pivot(index=['year','category'], columns='direction', values='quantity')
        .reset_index()
        .fillna(0)
    )

    # Ensure imports and exports columns exist (they may be missing if no data)
    if 'imports' not in yearly_trades.columns:
        yearly_trades['imports'] = 0
    if 'exports' not in yearly_trades.columns:
        yearly_trades['exports'] = 0

    fig0 = make_subplots(
        rows=2, cols=1,
        # shared_xaxes=True,
        vertical_spacing=0.15,
        subplot_titles=("", ""),
        row_heights=[0.5, 0.5]
    )

    for category in yearly_trades['category'].unique():
        cat_df = yearly_trades.query("category == @category")
        fig0.add_trace(go.Bar(
            x=cat_df['year'],
            y=cat_df['exports'],
            marker_color=cat_df['category'].map({k: v['base'] for k, v in CATEGORY_COLORS.items()}),
            name=category,
        ), row=1, col=1)

    for category in yearly_trades['category'].unique():
        cat_df = yearly_trades.query("category == @category")
        fig0.add_trace(go.Bar(
            x=cat_df['year'],
            y=cat_df['imports'],
            name=category,
            marker_color=cat_df['category'].map({k: v['base'] for k, v in CATEGORY_COLORS.items()}),
            showlegend=False,
        ), row=2, col=1)

    years = yearly_trades['year'].unique()
    y2_max = yearly_trades['imports'].max() if len(yearly_trades) > 0 and 'imports' in yearly_trades.columns else 0

    apply_subplot_theme(
        fig0,
        title=f'Exports and Imports for {selected_countries} by Category',
        theme=theme,
        height=400,
        years=list(years),
        y2_max=y2_max,
    )

    st.plotly_chart(fig0, width='stretch')

    # Create tabs for exports and imports
    tab1, tab2 = st.tabs(["Exports Analysis", "Imports Analysis"])

    with tab1:
        st.header("Exports Analysis")
    
    # Time series of exports by HS code
    fig1 = px.bar(
        yearly_exports,
        x='year',
        y='quantity',
        color='product_label',
        labels={
            'quantity': 'Volume (tons)',
            'year': 'Year',
            'product_label': 'HS Code'
        },
        barmode='stack',
        color_discrete_sequence=[HS_CODE_COLORS[code] for code in selected_hs_codes],
        template=get_plotly_template(theme)
    )
    apply_chart_theme(
        fig1,
        title=f'Export Volumes for {selected_countries} by HS Code',
        theme=theme,
    )
    st.plotly_chart(fig1, width='stretch')

    # Top export destinations with category breakdown
    st.subheader("Top Export Destinations")
    
    # Add year selector
    available_years = sorted(exports['year'].unique(), reverse=True)  # Sort years descending
    selected_year = st.selectbox(
        'Select Year',
        available_years,
        index=0  # Default to most recent year
    )
    
    # Filter exports for selected year
    exports_selected_year = exports[exports['year'] == selected_year]
    
    # Calculate total quantities and get top 20 countries
    country_totals = (
        exports_selected_year
        .groupby('importer_name')['quantity']
        .sum()
        .sort_values(ascending=False)
        .head(20)
    )
    
    # Get the detailed breakdown for top countries
    top_exports = (
        exports_selected_year[exports_selected_year['importer_name'].isin(country_totals.index)]
        .groupby(['year','product','importer_name'])['quantity']
        .sum()
        .reset_index()
        .copy()  # Create a copy to avoid SettingWithCopyWarning
    )
    
    # Add HS code labels
    top_exports['product_label'] = top_exports['product'].map(hs_code_labels)
    
    # Sort the countries by their total volume
    country_order = country_totals.index.tolist()
    
    fig2 = px.bar(
        top_exports,
        x='importer_name',
        y='quantity',
        color='product_label',
        labels={
            'quantity': 'Volume (tons)',
            'importer_name': 'Importing Country',
            'product_label': 'HS Code'
        },
        color_discrete_sequence=[HS_CODE_COLORS[code] for code in selected_hs_codes],
        category_orders={'importer_name': country_order},
        template=get_plotly_template(theme)
    )
    apply_chart_theme(
        fig2,
        title=f'Top Export Destinations for {selected_countries} ({selected_year})',
        theme=theme,
        x_tick_angle=30,
    )
    st.plotly_chart(fig2, width='stretch')

    with tab2:
        st.header("Imports Analysis")
        
        # Time series of imports by HS code
        fig3 = px.bar(
            yearly_imports,
            x='year',
            y='quantity',
            color='product_label',
            labels={
                'quantity': 'Volume (tons)',
                'year': 'Year',
                'product_label': 'HS Code'
            },
            barmode='stack',
            color_discrete_sequence=[HS_CODE_COLORS[code] for code in selected_hs_codes],
            template=get_plotly_template(theme)
        )
        apply_chart_theme(
            fig3,
            title=f'Import Volumes for {selected_countries} by HS Code',
            theme=theme,
        )
        st.plotly_chart(fig3, width='stretch')

        # Top import sources with category breakdown
        st.subheader("Top Import Sources")
    # Add year selector for imports
    available_years = sorted(imports['year'].unique(), reverse=True)  # Sort years descending
    selected_year_imports = st.selectbox(
        'Select Year',
        available_years,
        index=0,  # Changed to 0 to default to most recent year
        key='import_year_selector'
    )
    
    # Filter imports for selected year
    imports_selected_year = imports[imports['year'] == selected_year_imports]
    
    # Calculate total quantities and get top 20 countries
    country_totals = (
        imports_selected_year
        .groupby('exporter_name')['quantity']
        .sum()
        .sort_values(ascending=False)
        .head(20)
    )
    
    # Get the detailed breakdown for top countries
    top_imports = (
        imports_selected_year[imports_selected_year['exporter_name'].isin(country_totals.index)]
        .groupby(['year','product','exporter_name'])['quantity']
        .sum()
        .reset_index()
        .copy()
    )
    
    # Add HS code labels
    top_imports['product_label'] = top_imports['product'].map(hs_code_labels)
    
    # Sort the countries by their total volume
    country_order = country_totals.index.tolist()
    
    fig4 = px.bar(
        top_imports,
        x='exporter_name',
        y='quantity',
        color='product_label',
        labels={
            'quantity': 'Volume (tons)',
            'exporter_name': 'Exporting Country',
            'product_label': 'HS Code'
        },
        color_discrete_sequence=[HS_CODE_COLORS[code] for code in selected_hs_codes],
        category_orders={'exporter_name': country_order},
        template=get_plotly_template(theme)
    )
    apply_chart_theme(
        fig4,
        title=f'Top Import Sources for {selected_countries} ({selected_year_imports})',
        theme=theme,
        x_tick_angle=30,
    )
    st.plotly_chart(fig4, width='stretch')

    # Add after the filters section
    st.sidebar.subheader("Download Data")
    filtered_data = df_filtered[
        (df_filtered['exporter_name'] == country) |
        (df_filtered['importer_name'] == country)
    ] if country else df_filtered[
        (df_filtered['exporter_name'].isin(countries)) |
        (df_filtered['importer_name'].isin(countries))
    ]

    if st.sidebar.button('Download Filtered Data'):
        csv = filtered_data.to_csv(index=False)
        st.sidebar.download_button(
            label="Click to Download",
            data=csv,
            file_name=f"lead_trade_{selected_countries}_{selected_years[0]}-{selected_years[1]}.csv",
            mime='text/csv'
        )

    # Add at the very bottom of the file, after all other content
    st.markdown("---")
    st.markdown("<h2 id='product-definitions'>Product Definitions</h2>", unsafe_allow_html=True)
    st.markdown("Our analysis is based on [Harmonized System (HS) codes](https://www.wcotradetools.org/en/harmonized-system), which are a global standard for classifying traded goods.")

    for category, products in HS_CODE_CATEGORIES.items():
        st.markdown(f"### {category}")
        for hs_code, name in products:
            st.markdown(f"**{hs_code} - {name}**  \n{PRODUCT_DEFINITIONS[hs_code]}")




if __name__ == "__main__":
    main()
