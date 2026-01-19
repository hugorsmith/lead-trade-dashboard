"""
Tests for data loading functionality.
"""
import pytest
import pandas as pd
from pathlib import Path
from src.data_loader import load_trade_data, load_country_data


class TestDataLoading:
    """Test suite for data loading operations."""
    
    def test_trade_data_file_exists(self):
        """Verify that the trade data CSV file exists."""
        data_path = Path('lead_trade_data.csv')
        assert data_path.exists(), "lead_trade_data.csv not found"
    
    def test_country_data_file_exists(self):
        """Verify that the country data CSV file exists."""
        data_path = Path('countries.csv')
        assert data_path.exists(), "countries.csv not found"
    
    def test_load_trade_data_returns_dataframe(self):
        """Test that load_trade_data returns a valid DataFrame."""
        df = load_trade_data()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0, "Trade data is empty"
    
    def test_load_country_data_returns_dataframe(self):
        """Test that load_country_data returns a valid DataFrame."""
        df = load_country_data()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0, "Country data is empty"
    
    def test_trade_data_has_required_columns(self):
        """Verify trade data has all required columns."""
        df = load_trade_data()
        required_columns = [
            'year', 'exporter', 'importer', 'product', 
            'quantity', 'value', 'exporter_name', 'importer_name'
        ]
        for col in required_columns:
            assert col in df.columns, f"Missing required column: {col}"
    
    def test_country_data_has_required_columns(self):
        """Verify country data has all required columns."""
        df = load_country_data()
        required_columns = ['name', 'region', 'subregion']
        for col in required_columns:
            assert col in df.columns, f"Missing required column: {col}"


class TestEncodingFixes:
    """Test suite for encoding fixes."""
    
    def test_turkiye_exists_in_actual_data(self):
        """Test that Türkiye exists in the actual trade data after encoding fix."""
        df = load_trade_data()
        
        # Check that Türkiye appears in the data
        turkey_exports = df[df['exporter_name'] == 'Türkiye']
        turkey_imports = df[df['importer_name'] == 'Türkiye']
        
        assert len(turkey_exports) > 0, "Türkiye not found as exporter after encoding fix"
        assert len(turkey_imports) > 0, "Türkiye not found as importer after encoding fix"
    
    def test_turkiye_in_countries_csv(self):
        """Verify Türkiye is in countries.csv."""
        df = load_country_data()
        assert 'Türkiye' in df['name'].values, "Türkiye not found in countries.csv"


class TestDataProcessing:
    """Test suite for data processing steps."""
    
    def test_product_codes_are_padded(self):
        """Test that product codes are padded to 6 digits in loaded data."""
        df = load_trade_data()
        assert df['product'].str.len().eq(6).all(), "Not all product codes are 6 digits"
    
    def test_categories_assigned(self):
        """Test that categories are assigned in loaded data."""
        df = load_trade_data()
        assert 'category' in df.columns
        # Test a few known mappings
        assert df[df['product'] == '260700']['category'].iloc[0] == 'Ores & Concentrates'
        assert df[df['product'] == '780110']['category'].iloc[0] == 'New Lead'


class TestDataValidation:
    """Test suite for data validation."""
    
    def test_no_null_values_in_required_columns(self):
        """Test that required columns have no null values.

        Note: 'quantity' is excluded because ~1900 records have value but no weight data.
        This is expected in trade data where monetary value is reported without physical quantity.
        """
        df = load_trade_data()
        # quantity excluded - nulls are expected (records with value but no weight)
        required_columns = ['year', 'product', 'exporter_name', 'importer_name']

        for col in required_columns:
            assert df[col].notna().all(), f"Found null values in {col}"
    
    def test_valid_year_range(self):
        """Test that years are within expected range."""
        df = load_trade_data()
        assert df['year'].min() >= 2000, "Year is too old"
        assert df['year'].max() <= 2030, "Year is in the future"
    
    def test_product_codes_are_6_digits(self):
        """Test that all product codes are 6 digits."""
        df = load_trade_data()
        assert df['product'].str.len().eq(6).all(), "Not all product codes are 6 digits"
    
    def test_quantity_values_are_positive(self):
        """Test that quantity values are non-negative (excluding nulls)."""
        df = load_trade_data()
        # Exclude nulls - they're tested separately and are expected
        non_null = df[df['quantity'].notna()]
        assert (non_null['quantity'] >= 0).all(), "All quantities should be non-negative"

    def test_quantity_nulls_are_documented(self):
        """Document that some records have null quantities (value without weight).

        This is expected in trade data - some records report monetary value
        but not physical quantity/weight. These records still have valid 'value' data.
        """
        df = load_trade_data()
        null_count = df['quantity'].isna().sum()

        # There should be some nulls (around 1900 in current data)
        assert null_count > 0, "Expected some null quantities in trade data"

        # But nulls should still have value data
        nulls = df[df['quantity'].isna()]
        assert nulls['value'].notna().all(), "Records with null quantity should have value"

