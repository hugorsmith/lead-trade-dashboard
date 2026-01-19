"""
Shared test fixtures for the lead trade dashboard tests.
"""
import pytest
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_trade_data():
    """Create sample trade data for testing."""
    return pd.DataFrame({
        'year': [2020, 2020, 2021, 2021, 2022, 2022],
        'exporter': [156, 156, 156, 792, 792, 792],
        'importer': [840, 840, 840, 840, 840, 156],
        'exporter_name': ['China', 'China', 'China', 'Türkiye', 'Türkiye', 'Türkiye'],
        'importer_name': ['USA', 'USA', 'USA', 'USA', 'USA', 'China'],
        'product': ['780110', '850710', '780110', '850710', '854810', '780110'],
        'quantity': [1000.0, 500.0, 1200.0, 300.0, 450.0, 200.0],
        'value': [50000, 25000, 60000, 15000, 22500, 10000]
    })


@pytest.fixture
def sample_trade_data_with_encoding_issue():
    """Create sample trade data with encoding issues (TÃ¼rkiye instead of Türkiye)."""
    return pd.DataFrame({
        'year': [2020, 2021, 2022],
        'exporter_name': ['TÃ¼rkiye', 'TÃ¼rkiye', 'China'],
        'importer_name': ['USA', 'Germany', 'TÃ¼rkiye'],
        'product': ['780110', '850710', '854810'],
        'quantity': [100.0, 200.0, 300.0],
        'value': [5000, 10000, 15000]
    })


@pytest.fixture
def sample_country_data():
    """Create sample country data for testing."""
    return pd.DataFrame({
        'name': ['China', 'USA', 'Türkiye', 'Germany', 'Brazil'],
        'region': ['Asia', 'Americas', 'Asia', 'Europe', 'Americas'],
        'subregion': ['Eastern Asia', 'Northern America', 'Western Asia', 'Western Europe', 'South America'],
        'intermediate_region': [None, None, None, None, None],
        'iso3': ['CHN', 'USA', 'TUR', 'DEU', 'BRA']
    })


@pytest.fixture
def hs_code_categories():
    """Sample HS code categories for testing."""
    return {
        'Ores & Concentrates': [('260700', 'Lead ores and concentrates')],
        'New Lead': [
            ('780110', 'Refined lead - unwrought'),
            ('780191', 'Other unwrought lead, with antimony'),
            ('780199', 'Other unrefined lead')
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


@pytest.fixture
def hs_to_category(hs_code_categories):
    """Create HS code to category mapping."""
    return {
        hs_code: category
        for category, products in hs_code_categories.items()
        for hs_code, _ in products
    }
