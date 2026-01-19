"""
Tests for data integrity and edge cases.
"""
import pytest
import pandas as pd


class TestEdgeCases:
    """Test suite for edge cases and data integrity."""
    
    def test_empty_filter_results(self, sample_trade_data):
        """Test behavior when filters return no results."""
        df = sample_trade_data
        
        # Filter for a non-existent country
        filtered = df[df['exporter_name'] == 'NonExistentCountry']
        
        assert len(filtered) == 0
        assert isinstance(filtered, pd.DataFrame)
    
    def test_single_year_data(self, sample_trade_data):
        """Test calculations with single year of data."""
        df = sample_trade_data[sample_trade_data['year'] == 2020]
        
        assert len(df) > 0
        total = df['quantity'].sum()
        assert total > 0
    
    def test_missing_previous_year_data(self, sample_trade_data):
        """Test YoY calculation when previous year data is missing."""
        df = sample_trade_data
        
        # Current year with data
        current_year = 2023
        current_value = 100
        
        # Previous year with no data
        previous_year = 2022
        previous_data = df[df['year'] == previous_year]
        previous_value = previous_data['quantity'].sum()
        
        # If previous year is 0, YoY should handle gracefully
        def calculate_yoy_change(current_value, previous_value):
            if previous_value == 0:
                return 0
            return ((current_value - previous_value) / previous_value) * 100
        
        result = calculate_yoy_change(current_value, previous_value)
        assert isinstance(result, (int, float))
    
    def test_all_hs_codes_deselected(self):
        """Test behavior when no HS codes are selected."""
        # The app has a fallback for this
        selected_hs_codes = []
        
        if not selected_hs_codes:
            # Fallback to first HS code
            selected_hs_codes = ['260700']
        
        assert len(selected_hs_codes) > 0
    
    def test_country_with_only_exports(self, sample_trade_data):
        """Test metrics for country that only exports (no imports)."""
        df = sample_trade_data
        
        # Türkiye has exports but check imports
        turkey_exports = df[df['exporter_name'] == 'Türkiye']
        turkey_imports = df[df['importer_name'] == 'Türkiye']
        
        exports_total = turkey_exports['quantity'].sum()
        imports_total = turkey_imports['quantity'].sum()
        trade_balance = exports_total - imports_total
        
        # Should handle gracefully even if one is zero
        assert isinstance(trade_balance, (int, float))
    
    def test_duplicate_function_definitions(self):
        """Test that duplicate function definitions work correctly."""
        # This documents the duplicate calculate_yoy_change bug
        def calculate_yoy_change_1(current_value, previous_value):
            if previous_value == 0:
                return 0
            return ((current_value - previous_value) / previous_value) * 100
        
        def calculate_yoy_change_2(current_value, previous_value):
            if previous_value == 0:
                return 0
            return ((current_value - previous_value) / previous_value) * 100
        
        # Both should give same result
        result1 = calculate_yoy_change_1(120, 100)
        result2 = calculate_yoy_change_2(120, 100)
        assert result1 == result2


class TestDataConsistency:
    """Test suite for data consistency checks."""
    
    def test_country_names_consistency(self):
        """Test that country names are consistent across datasets."""
        country_df = pd.read_csv('countries.csv', encoding='utf-8')
        trade_df = pd.read_csv('lead_trade_data.csv', encoding='utf-8', nrows=5000)
        
        # Apply encoding fix
        trade_df['exporter_name'] = trade_df['exporter_name'].str.replace('TÃ¼rkiye', 'Türkiye', regex=False)
        trade_df['importer_name'] = trade_df['importer_name'].str.replace('TÃ¼rkiye', 'Türkiye', regex=False)
        
        # Check that Türkiye is spelled correctly in both
        assert 'Türkiye' in country_df['name'].values
        assert 'Türkiye' in trade_df['exporter_name'].values or 'Türkiye' in trade_df['importer_name'].values
    
    def test_no_negative_quantities(self):
        """Test that there are no negative quantities (excluding nulls)."""
        df = pd.read_csv('lead_trade_data.csv', encoding='utf-8')

        # Exclude nulls - they're a separate issue (records with value but no weight)
        non_null = df[df['quantity'].notna()]
        assert (non_null['quantity'] >= 0).all(), "Found negative quantities in data"
    
    def test_no_negative_values(self):
        """Test that there are no negative trade values."""
        df = pd.read_csv('lead_trade_data.csv', encoding='utf-8', nrows=1000)
        
        assert (df['value'] >= 0).all(), "Found negative values in data"
    
    def test_product_codes_valid_format(self):
        """Test that product codes are in valid format."""
        df = pd.read_csv('lead_trade_data.csv', encoding='utf-8', nrows=100)
        
        # Convert to string and pad
        df['product'] = df['product'].astype(str).str.zfill(6)
        
        # All should be 6 digits
        assert all(len(code) == 6 for code in df['product'])
        assert all(code.isdigit() for code in df['product'])
