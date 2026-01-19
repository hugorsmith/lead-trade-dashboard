"""Tests for calculation functions."""
import pytest
import pandas as pd
from src.calculations import calculate_yoy_change


class TestYearOverYearCalculations:
    """Test suite for YoY change calculations."""
    
    @pytest.mark.parametrize("current,previous,expected", [
        (120, 100, 20.0),      # 20% growth
        (80, 100, -20.0),      # 20% decline
        (100, 0, 0),           # Handle zero division
        (100, 100, 0.0),       # No change
        (0, 100, -100.0),      # Zero current value
        (150, 100, 50.0),      # 50% growth
        (50, 100, -50.0),      # 50% decline
    ])
    def test_yoy_change(self, current, previous, expected):
        """Test YoY calculation with various scenarios."""
        result = calculate_yoy_change(current, previous)
        assert result == pytest.approx(expected), f"YoY change from {previous} to {current} should be {expected}%"


class TestTradeMetrics:
    """Test suite for trade metric calculations."""
    
    def test_trade_balance_calculation(self, sample_trade_data):
        """Test trade balance calculation (exports - imports)."""
        df = sample_trade_data
        
        # Calculate exports and imports for China
        exports = df[df['exporter_name'] == 'China']['quantity'].sum()
        imports = df[df['importer_name'] == 'China']['quantity'].sum()
        trade_balance = exports - imports  # Simple subtraction, no need for function
        
        assert trade_balance == exports - imports
        assert isinstance(trade_balance, (int, float))
    
    def test_total_export_volume(self, sample_trade_data):
        """Test total export volume calculation."""
        df = sample_trade_data
        
        # Filter for a specific country and year
        exports = df[(df['exporter_name'] == 'China') & (df['year'] == 2020)]
        total = exports['quantity'].sum()
        
        assert total > 0
        assert isinstance(total, (int, float))
    
    def test_total_import_volume(self, sample_trade_data):
        """Test total import volume calculation."""
        df = sample_trade_data
        
        # Filter for a specific country and year
        imports = df[(df['importer_name'] == 'USA') & (df['year'] == 2020)]
        total = imports['quantity'].sum()
        
        assert total > 0
        assert isinstance(total, (int, float))
    
    def test_trading_partners_count(self, sample_trade_data):
        """Test counting unique trading partners."""
        df = sample_trade_data
        
        # For China in 2020
        china_2020 = df[(df['exporter_name'] == 'China') & (df['year'] == 2020)]
        partners = set(china_2020['importer_name'].unique())
        
        assert len(partners) > 0
        assert 'USA' in partners


class TestDataAggregations:
    """Test suite for data aggregation operations."""
    
    def test_yearly_aggregation(self, sample_trade_data):
        """Test aggregating data by year."""
        df = sample_trade_data
        
        yearly = df.groupby('year')['quantity'].sum().reset_index()
        
        assert len(yearly) > 0
        assert 'year' in yearly.columns
        assert 'quantity' in yearly.columns
        assert yearly['quantity'].sum() == df['quantity'].sum()
    
    def test_product_aggregation(self, sample_trade_data):
        """Test aggregating data by product."""
        df = sample_trade_data
        
        by_product = df.groupby('product')['quantity'].sum().reset_index()
        
        assert len(by_product) > 0
        assert by_product['quantity'].sum() == df['quantity'].sum()
    
    def test_category_assignment(self, sample_trade_data, hs_to_category):
        """Test assigning categories to HS codes."""
        df = sample_trade_data.copy()
        
        df['category'] = df['product'].map(hs_to_category)
        
        # Check that categories are assigned
        assert 'category' in df.columns
        # Check that known HS codes have categories
        assert df[df['product'] == '780110']['category'].iloc[0] == 'New Lead'
        assert df[df['product'] == '850710']['category'].iloc[0] == 'New Batteries'
    
    def test_pivot_with_missing_data(self):
        """Test pivot operation when some categories are missing."""
        # Create data with only exports (no imports)
        df = pd.DataFrame({
            'year': [2020, 2021],
            'category': ['New Lead', 'New Batteries'],
            'direction': ['exports', 'exports'],
            'quantity': [100, 200]
        })
        
        pivoted = df.pivot(index=['year', 'category'], columns='direction', values='quantity').reset_index().fillna(0)
        
        # Ensure missing 'imports' column is handled
        if 'imports' not in pivoted.columns:
            pivoted['imports'] = 0
        if 'exports' not in pivoted.columns:
            pivoted['exports'] = 0
        
        assert 'imports' in pivoted.columns
        assert 'exports' in pivoted.columns
        assert (pivoted['imports'] == 0).all()
