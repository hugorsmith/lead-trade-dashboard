import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Lead Trade Analysis",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("Global Lead Trade Analysis Dashboard")
st.markdown("""
    This dashboard provides interactive visualizations of global lead metal trade data from 2012-2022.
    Select a country and HS codes to explore trade patterns by weight (tons).
""")

# Create a container div for both links
st.markdown("""
    <div style='display: flex; gap: 12px; align-items: center; margin-bottom: 20px;'>
        <a href='https://leadbatteries.substack.com/' target='_blank'>
            <button style='
                background-color: #FF4B4B;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.9rem;
                transition: background-color 0.3s;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            '>
                📚 Read More on Lead Battery Notes
            </button>
        </a>
        <a href='https://github.com/hugorsmith/lead-trade-data' style='
            color: #4A90E2;
            text-decoration: none;
            font-size: 0.9rem;
        '>
            🔗 Data Source
        </a>
    </div>
""", unsafe_allow_html=True)

# Add this color palette definition after the HS_CODE_CATEGORIES definition
CUSTOM_COLORS = [
    '#00C805',  # Bright green
    '#0FDDAF',  # Teal
    '#2B95FF',  # Bright blue
    '#665AFF',  # Purple
    '#FF5AE5',  # Pink
    '#FF5A8F',  # Rose
    '#FF7445',  # Orange
    '#FFB000',  # Gold
]

# Define the HS codes and their categories at the top level (before any functions)
HS_CODE_CATEGORIES = {
    'New Lead': [
        (260700, 'Lead ores and concentrates'),
        (780110, 'Refined lead - unwrought'),
        (780191, 'Other unwrought lead'),
        (780199, 'Other refined lead')
    ],
    'New Batteries': [
        (850710, 'New lead-acid batteries for starting engines'),
        (850720, 'Other new lead-acid batteries')
    ],
    'Used Batteries & Scrap': [
        (854810, 'Waste batteries'),
        (780200, 'Lead waste and scrap')
    ]
}

# Create a mapping dictionary for the category assignment
HS_TO_CATEGORY = {
    hs_code: category
    for category, products in HS_CODE_CATEGORIES.items()
    for hs_code, _ in products
}

# Load the data
@st.cache_data
def load_data():
    try:
        with st.spinner('Loading trade data...'):
            df = pd.read_csv('lead_trade_data.csv')
            df['product'] = df['product'].astype(int)
            df['category'] = df['product'].map(HS_TO_CATEGORY)
            return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

df = load_data()
if df is None:
    st.stop()

# Sidebar for filters
st.sidebar.header("Filters")

# Country selector
all_countries = sorted(list(set(df['exporter_name'].unique()) | set(df['importer_name'].unique())))
selected_country = st.sidebar.selectbox('Select a country:', all_countries)

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

# Update the data filtering
df_filtered = df[
    (df['product'].isin(selected_hs_codes)) & 
    (df['year'].between(selected_years[0], selected_years[1]))
]

# Create trade flows for selected country
exports = df_filtered[df_filtered['exporter_name'] == selected_country].copy()
imports = df_filtered[df_filtered['importer_name'] == selected_country].copy()

# Add key metrics at the top
st.subheader("Key Metrics (tons)")

# Add year selector for metrics
available_years = sorted(df_filtered['year'].unique(), reverse=True)  # Sort in descending order
selected_metrics_year = st.selectbox(
    'Select Year for Metrics',
    available_years,
    index=0,  # Default to first (most recent) year
    key='metrics_year_selector'
)

# Filter data for selected year
exports_year = exports[exports['year'] == selected_metrics_year]
imports_year = imports[imports['year'] == selected_metrics_year]

metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

with metrics_col1:
    total_exports = exports_year['quantity'].sum()
    def calculate_yoy_change(current_value, previous_value):
        if previous_value == 0:
            return 0
        return ((current_value - previous_value) / previous_value) * 100

    # Get previous year data
    previous_year = selected_metrics_year - 1
    exports_prev_year = exports[exports['year'] == previous_year]['quantity'].sum()
    import_change = calculate_yoy_change(total_exports, exports_prev_year)
    st.metric(
        "Total Export Volume", 
        f"{total_exports:,.0f} mt",
        f"{import_change:+.1f}% vs prev year"
    )

with metrics_col2:
    total_imports = imports_year['quantity'].sum()
    def calculate_yoy_change(current_value, previous_value):
        if previous_value == 0:
            return 0
        return ((current_value - previous_value) / previous_value) * 100

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

# Create tabs for exports and imports
tab1, tab2 = st.tabs(["Exports Analysis", "Imports Analysis"])

with tab1:
    st.header("Exports Analysis")
    
    # Time series of exports by HS code
    yearly_exports = (
        exports.groupby(['year', 'category', 'product'])['quantity']
        .sum()
        .reset_index()
    )
    
    # Create labels for the HS codes
    hs_code_labels = {
        code: f"{code} - {desc}"
        for category, products in HS_CODE_CATEGORIES.items()
        for code, desc in products
    }
    yearly_exports['product_label'] = yearly_exports['product'].map(hs_code_labels)
    
    fig1 = px.bar(
        yearly_exports,
        x='year',
        y='quantity',
        color='product_label',
        title=f'Export Volumes for {selected_country} by HS Code',
        labels={
            'quantity': 'Volume (tons)',
            'year': 'Year',
            'product_label': 'HS Code'
        },
        barmode='stack',
        color_discrete_sequence=CUSTOM_COLORS
    )
    # Customize the layout
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            title="HS Codes",
            orientation="h",
            yanchor="bottom",
            y=-0.5,
            xanchor="center",
            x=0.5
        ),
        font=dict(color='#E0E0E0'),
        title_font_color='#E0E0E0',
        xaxis=dict(gridcolor='rgba(128,128,128,0.1)', linecolor='rgba(128,128,128,0.2)'),
        yaxis=dict(gridcolor='rgba(128,128,128,0.1)', linecolor='rgba(128,128,128,0.2)')
    )
    st.plotly_chart(fig1, use_container_width=True)

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
        title=f'Top Export Destinations for {selected_country} ({selected_year})',
        labels={
            'quantity': 'Volume (tons)',
            'importer_name': 'Importing Country',
            'product_label': 'HS Code'
        },
        color_discrete_sequence=CUSTOM_COLORS,
        category_orders={'importer_name': country_order}  # Explicitly set the order
    )
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            title="HS Codes",
            orientation="h",
            yanchor="bottom",
            y=-0.5,
            xanchor="center",
            x=0.5
        ),
        font=dict(color='#E0E0E0'),
        title_font_color='#E0E0E0',
        xaxis=dict(
            gridcolor='rgba(128,128,128,0.1)', 
            linecolor='rgba(128,128,128,0.2)',
            tickangle=30,  # Less extreme angle
            tickfont=dict(size=9),  # Smaller font
            automargin=True  # Automatically adjust margins
        ),
        yaxis=dict(
            gridcolor='rgba(128,128,128,0.1)', 
            linecolor='rgba(128,128,128,0.2)'
        ),
        margin=dict(b=100, l=50, r=50, t=50),  # Explicit margins
        height=600  # Make the chart taller
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.header("Imports Analysis")
    
    # Time series of imports by HS code
    yearly_imports = (
        imports.groupby(['year', 'category', 'product'])['quantity']
        .sum()
        .reset_index()
    )
    
    yearly_imports['product_label'] = yearly_imports['product'].map(hs_code_labels)
    
    fig3 = px.bar(
        yearly_imports,
        x='year',
        y='quantity',
        color='product_label',
        title=f'Import Volumes for {selected_country} by HS Code',
        labels={
            'quantity': 'Volume (tons)',
            'year': 'Year',
            'product_label': 'HS Code'
        },
        barmode='stack',
        color_discrete_sequence=CUSTOM_COLORS
    )
    fig3.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            title="HS Codes",
            orientation="h",
            yanchor="bottom",
            y=-0.5,
            xanchor="center",
            x=0.5
        ),
        font=dict(color='#E0E0E0'),
        title_font_color='#E0E0E0',
        xaxis=dict(gridcolor='rgba(128,128,128,0.1)', linecolor='rgba(128,128,128,0.2)'),
        yaxis=dict(gridcolor='rgba(128,128,128,0.1)', linecolor='rgba(128,128,128,0.2)')
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Top import sources with category breakdown
    st.subheader("Top Import Sources")
    
    # Add year selector for imports
    selected_year_imports = st.selectbox(
        'Select Year',
        available_years,
        index=len(available_years)-1,
        key='import_year_selector'
    )
    
    # Filter imports for selected year
    imports_selected_year = imports[imports['year'] == selected_year_imports]
    
    # Calculate total quantities per country to determine top sources
    source_totals = (
        imports_selected_year
        .groupby('exporter_name')['quantity']
        .sum()
        .sort_values(ascending=False)
        .head(20)
        .index.tolist()
    )
    
    # Get detailed breakdown by product for these countries
    top_imports = (
        imports_selected_year[imports_selected_year['exporter_name'].isin(source_totals)]
        .groupby(['exporter_name', 'product'])['quantity']
        .sum()
        .reset_index()
    )
    
    # Add HS code labels
    top_imports['product_label'] = top_imports['product'].map(hs_code_labels)
    
    # Sort the data frame to match the source_totals order
    top_imports['exporter_name'] = pd.Categorical(
        top_imports['exporter_name'], 
        categories=source_totals, 
        ordered=True
    )
    top_imports = top_imports.sort_values('exporter_name')

    fig4 = px.bar(
        top_imports,
        x='exporter_name',
        y='quantity',
        color='product_label',
        title=f'Top Import Sources for {selected_country} ({selected_year_imports})',
        labels={
            'quantity': 'Volume (tons)',
            'exporter_name': 'Exporting Country',
            'product_label': 'HS Code'
        },
        color_discrete_sequence=CUSTOM_COLORS
    )
    fig4.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            title="HS Codes",
            orientation="h",
            yanchor="bottom",
            y=-0.5,
            xanchor="center",
            x=0.5
        ),
        font=dict(color='#E0E0E0'),
        title_font_color='#E0E0E0',
        xaxis=dict(gridcolor='rgba(128,128,128,0.1)', linecolor='rgba(128,128,128,0.2)'),
        yaxis=dict(gridcolor='rgba(128,128,128,0.1)', linecolor='rgba(128,128,128,0.2)')
    )
    st.plotly_chart(fig4, use_container_width=True)

# Add this at the beginning of the file, after the st.set_page_config
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
    .stMetric label {
        color: #E0E0E0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Add after the filters section
st.sidebar.subheader("Download Data")
filtered_data = df_filtered[
    (df_filtered['exporter_name'] == selected_country) |
    (df_filtered['importer_name'] == selected_country)
]

if st.sidebar.button('Download Filtered Data'):
    csv = filtered_data.to_csv(index=False)
    st.sidebar.download_button(
        label="Click to Download",
        data=csv,
        file_name=f"lead_trade_{selected_country}_{selected_years[0]}-{selected_years[1]}.csv",
        mime='text/csv'
    ) 