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

# Create a container div for text and both links
st.markdown("""
    <div>
        Based on global lead metal trade data from 2012-2023.
        Select a country and HS codes to explore trade patterns by weight (tons).
    </div>
    <br>
    <div style='display: flex; gap: 20px; align-items: center; margin-bottom: 20px;'>
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

# Define the HS codes and their categories at the top level (before any color definitions)
HS_CODE_CATEGORIES = {
    'Ores & Concentrates': [
        ('260700', 'Lead ores and concentrates')
    ],
    'New Lead': [
        ('780110', 'Refined lead - unwrought'),
        ('780191', 'Other unwrought lead'),
        ('780199', 'Other refined lead')
    ],
    'New Batteries': [
        ('850710', 'New lead-acid batteries for starting engines'),
        ('850720', 'Other new lead-acid batteries')
    ],
    'Used Batteries & Scrap': [
        ('854810', 'Waste batteries'),
        ('780200', 'Lead waste and scrap')
    ]
}

# Add color definitions after HS_CODE_CATEGORIES
CATEGORY_COLORS = {
    'Ores & Concentrates': {
        'base': '#A0522D',  # Sienna brown
        'codes': {
            '260700': '#A0522D'  # Same as base since only one code
        }
    },
    'New Lead': {
        'base': '#8C8C8C',  # Base gray
        'codes': {
            '780110': '#707070',  # Darker gray
            '780191': '#8C8C8C',  # Base gray
            '780199': '#A5A5A5'   # Lighter gray
        }
    },
    'New Batteries': {
        'base': '#228B22',  # Forest green
        'codes': {
            '850710': '#1B6B1B',  # Darker green
            '850720': '#3DA23D'   # Lighter green
        }
    },
    'Used Batteries & Scrap': {
        'base': '#FF7F00',  # Bright orange
        'codes': {
            '854810': '#E66E00',  # Darker orange
            '780200': '#FF9933'   # Lighter orange
        }
    }
}

# Create a flat mapping of HS codes to colors for easy lookup
HS_CODE_COLORS = {
    hs_code: category_data['codes'][hs_code]
    for category, category_data in CATEGORY_COLORS.items()
    for hs_code in category_data['codes']
}

# Create a list of category colors in the same order as categories
CATEGORY_COLOR_LIST = [CATEGORY_COLORS[cat]['base'] for cat in HS_CODE_CATEGORIES.keys()]

# Create theme-aware plotly template
def get_plotly_template():
    is_light_theme = st.get_option("theme.base") == "light"
    if is_light_theme:
        return 'plotly'  # Use default light theme
    else:
        return 'plotly_dark'  # Use built-in dark theme

# Create a mapping dictionary for the category assignment
HS_TO_CATEGORY = {
    hs_code: category
    for category, products in HS_CODE_CATEGORIES.items()
    for hs_code, _ in products
}

# Load the data
@st.cache_data
def load_trade_data():
    try:
        with st.spinner('Loading trade data...'):
            df = pd.read_csv('lead_trade_data.csv')
            # Convert product codes to strings with leading zeros preserved
            df['product'] = df['product'].astype(str).str.zfill(6)
            df['category'] = df['product'].map(HS_TO_CATEGORY)
            return df
    except Exception as e:
        st.error(f"Error loading trade data: {str(e)}")
        return None
    
@st.cache_data
def load_country_data():
    try:
        with st.spinner('Loading trade data...'):
            country_df = pd.read_csv('countries.csv')
            return country_df
    except Exception as e:
        st.error(f"Error loading country data: {str(e)}")
        return None, None

df = load_trade_data()
country_df = load_country_data()
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
    regions = sorted(country_df.region.drop_duplicates().to_list())
    region = st.selectbox("Region", regions, index=None)

with subregion_col:
    subregions = country_df[country_df.subregion.notna()]
    subregions = subregions.query("region == @region or @region == @region")
    subregions = sorted(subregions.subregion.drop_duplicates().to_list())
    subregion = st.selectbox("Sub-region", subregions, index=None)

with intermediate_col:
    intermediate = country_df[country_df.intermediate_region.notna()]
    intermediate = intermediate.query("(region == @region or @region == @region) and (subregion == @subregion or @subregion == @subregion)")
    intermediate = sorted(intermediate.intermediate_region.drop_duplicates().to_list())
    intermediate_region = st.selectbox("Intermediate Region", intermediate, index=None)

with country_col:
    countries = country_df[country_df.name.notna()]
    countries = countries.query("""
        (region == @region or @region == @region) and \
        (subregion == @subregion or @subregion == @subregion) and \
        (intermediate_region == @intermediate_region or @intermediate_region == @intermediate_region)
    """)
    countries = sorted(countries.name.drop_duplicates().to_list())
    country = st.selectbox("Country", countries, index=None)

# Update the data filtering
df_filtered = df[
    (df['product'].isin(selected_hs_codes)) & 
    (df['year'].between(selected_years[0], selected_years[1]))
]

# Create trade flows for selected country
if country:
    exports = df_filtered[df_filtered.exporter_name == country].copy()
    imports = df_filtered[df_filtered.importer_name == country].copy()
else:
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
st.subheader("Key Metrics (tons)")

# Add year selector for metrics
available_years = sorted(df_filtered['year'].unique(), reverse=True)  # Sort in descending order
selected_metrics_year = df_filtered.year.max()

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

# Create labels for the HS codes
hs_code_labels = {
    code: f"{code} - {desc}"
    for category, products in HS_CODE_CATEGORIES.items()
    for code, desc in products
}

yearly_exports = (
    exports.groupby(['year', 'category', 'product'])['quantity']
    .sum()
    .reset_index()
    .assign(product_label = lambda x: x['product'].map(hs_code_labels))
)

yearly_imports = (
    imports.groupby(['year', 'category', 'product'])['quantity']
    .sum()
    .reset_index()
    .assign(product_label = lambda x: x['product'].map(hs_code_labels))
)

# Show trade imbalance
yearly_imports_cat = (
    yearly_imports
    .groupby(['year', 'category'])
    .sum()
    .reset_index()
)

yearly_exports_cat = (
    yearly_exports
    .groupby(['year', 'category'])
    .sum()
    .reset_index()
)

from plotly.subplots import make_subplots

fig0 = make_subplots(
    rows=2, cols=1,
    # shared_xaxes=True,
    vertical_spacing=0.15,
    subplot_titles=("", ""),
    row_heights=[0.5, 0.5]
)

for category in yearly_exports_cat['category'].unique():
    cat_df = yearly_exports_cat.query("category == @category")
    fig0.add_trace(go.Bar(
        x=cat_df['year'],
        y=cat_df['quantity'],
        marker_color=cat_df['category'].map({k: v['base'] for k, v in CATEGORY_COLORS.items()}),
        name=category,
    ), row=1, col=1,)

for category in yearly_imports_cat['category'].unique():
    cat_df = yearly_imports_cat.query("category == @category")
    fig0.add_trace(go.Bar(
        x=cat_df['year'],
        y=cat_df['quantity'],
        name=category,
        marker_color=cat_df['category'].map({k: v['base'] for k, v in CATEGORY_COLORS.items()}),
        showlegend=False,
    ), row=2, col=1,)

# Customize the layout
fig0.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    legend=dict(
        title="",
        orientation="h",
        y=1.1,
        x=0
    ),
    # Only apply custom colors in dark mode
    font=dict(
        color='#E0E0E0' if st.get_option("theme.base") == "dark" else None,
        size=12
    ),
    title=dict(
        text=f'Export-Import Imbalance for {selected_countries} by Category',
        font=dict(
            color='#E0E0E0' if st.get_option("theme.base") == "dark" else None,
            size=16
        )
    ),
    xaxis=dict(
        gridcolor='rgba(128,128,128,0.1)', 
        linecolor='rgba(128,128,128,0.2)',
        title="",
        tickvals=yearly_exports_cat['year'].unique(),
        ticktext=yearly_exports_cat['year'].astype(str).unique(),
        domain=[0,1]
    ),
    xaxis2=dict(
        gridcolor='rgba(128,128,128,0.1)', 
        linecolor='rgba(128,128,128,0.2)',
        title="",
        tickvals=cat_df['year'].unique(),
        ticktext=cat_df['year'].astype(str).unique(),
        domain=[0,1],
        showticklabels=False
    ),
    yaxis=dict(
        gridcolor='rgba(128,128,128,0.1)', 
        linecolor='rgba(128,128,128,0.2)',
        title="Exports (tons)",
        # zeroline=True,  # Added: more visible zero line
        # zerolinewidth=2  # Added: thicker zero line
    ),
    yaxis2=dict(
        gridcolor='rgba(128,128,128,0.1)', 
        linecolor='rgba(128,128,128,0.2)',
        title="Imports (tons)",
        range=[yearly_imports_cat.groupby(['year'])['quantity'].sum().reset_index().quantity.max(), 0]
    ),
    barmode="stack",
    margin=dict(b=120, l=50, r=50, t=50),
    height=400
)

st.plotly_chart(fig0, use_container_width=True)

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
        template=get_plotly_template()
    )
    # Customize the layout
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            title="HS Codes",
            orientation="h",
            yanchor="bottom",
            y=-0.55,
            xanchor="center",
            x=0.5
        ),
        # Only apply custom colors in dark mode
        font=dict(
            color='#E0E0E0' if st.get_option("theme.base") == "dark" else None,
            size=12
        ),
        title=dict(
            text=f'Export Volumes for {selected_countries} by HS Code',
            font=dict(
                color='#E0E0E0' if st.get_option("theme.base") == "dark" else None,
                size=16
            )
        ),
        xaxis=dict(
            gridcolor='rgba(128,128,128,0.1)', 
            linecolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            gridcolor='rgba(128,128,128,0.1)', 
            linecolor='rgba(128,128,128,0.2)'
        ),
        margin=dict(b=120, l=50, r=50, t=50),
        height=550
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
        category_orders={'importer_name': country_order},  # Explicitly set the order
        template=get_plotly_template()
    )
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            title="HS Codes",
            orientation="h",
            yanchor="bottom",
            y=-0.55,
            xanchor="center",
            x=0.5
        ),
        # Only apply custom colors in dark mode
        font=dict(
            color='#E0E0E0' if st.get_option("theme.base") == "dark" else None,
            size=12
        ),
        title=dict(
            text=f'Top Export Destinations for {selected_countries} ({selected_year})',
            font=dict(
                color='#E0E0E0' if st.get_option("theme.base") == "dark" else None,
                size=16
            )
        ),
        xaxis=dict(
            gridcolor='rgba(128,128,128,0.1)', 
            linecolor='rgba(128,128,128,0.2)',
            tickangle=30,
            tickfont=dict(size=9),
            automargin=True
        ),
        yaxis=dict(
            gridcolor='rgba(128,128,128,0.1)', 
            linecolor='rgba(128,128,128,0.2)'
        ),
        margin=dict(b=120, l=50, r=50, t=50),
        height=550
    )
    st.plotly_chart(fig2, use_container_width=True)

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
        template=get_plotly_template()
    )
    fig3.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            title="HS Codes",
            orientation="h",
            yanchor="bottom",
            y=-0.55,
            xanchor="center",
            x=0.5
        ),
        # Only apply custom colors in dark mode
        font=dict(
            color='#E0E0E0' if st.get_option("theme.base") == "dark" else None,
            size=12
        ),
        title=dict(
            text=f'Import Volumes for {selected_countries} by HS Code',
            font=dict(
                color='#E0E0E0' if st.get_option("theme.base") == "dark" else None,
                size=16
            )
        ),
        xaxis=dict(
            gridcolor='rgba(128,128,128,0.1)', 
            linecolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            gridcolor='rgba(128,128,128,0.1)', 
            linecolor='rgba(128,128,128,0.2)'
        ),
        margin=dict(b=120, l=50, r=50, t=50),
        height=550
    )
    st.plotly_chart(fig3, use_container_width=True)

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
        category_orders={'exporter_name': country_order},  # Explicitly set the order
        template=get_plotly_template()
    )
    
    # Rest of the layout remains the same
    fig4.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            title="HS Codes",
            orientation="h",
            yanchor="bottom",
            y=-0.55,
            xanchor="center",
            x=0.5
        ),
        font=dict(
            color='#E0E0E0' if st.get_option("theme.base") == "dark" else None,
            size=12
        ),
        title=dict(
            text=f'Top Import Sources for {selected_countries} ({selected_year_imports})',
            font=dict(
                color='#E0E0E0' if st.get_option("theme.base") == "dark" else None,
                size=16
            )
        ),
        xaxis=dict(
            gridcolor='rgba(128,128,128,0.1)', 
            linecolor='rgba(128,128,128,0.2)',
            tickangle=30,  # Added to match exports
            tickfont=dict(size=9),  # Added to match exports
            automargin=True  # Added to match exports
        ),
        yaxis=dict(
            gridcolor='rgba(128,128,128,0.1)', 
            linecolor='rgba(128,128,128,0.2)'
        ),
        margin=dict(b=120, l=50, r=50, t=50),
        height=550
    )
    st.plotly_chart(fig4, use_container_width=True)

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