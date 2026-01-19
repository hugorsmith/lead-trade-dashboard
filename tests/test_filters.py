"""
Tests for filtering logic.
"""
import pytest
import pandas as pd
from src.filters import (
    filter_by_geography,

    get_available_subregions,
    get_available_countries
)


@pytest.fixture
def sample_geo_data():
    """Sample country/geographic data for testing."""
    return pd.DataFrame({
        'name': ['China', 'USA', 'Germany', 'Türkiye', 'Brazil'],
        'region': ['Asia', 'Americas', 'Europe', 'Asia', 'Americas'],
        'subregion': ['Eastern Asia', 'Northern America', 'Western Europe', 'Western Asia', 'South America']
    })


@pytest.fixture
def sample_trade_df():
    """Sample trade data for testing filters."""
    return pd.DataFrame({
        'year': [2020, 2020, 2021, 2021, 2022],
        'product': ['780110', '850710', '780110', '854810', '260700'],
        'exporter_name': ['China', 'USA', 'Germany', 'China', 'Brazil'],
        'importer_name': ['USA', 'Germany', 'China', 'USA', 'China'],
        'quantity': [1000, 500, 800, 300, 1200],
        'region': ['Asia', 'Americas', 'Europe', 'Asia', 'Americas'],
        'subregion': ['Eastern Asia', 'Northern America', 'Western Europe', 'Eastern Asia', 'South America']
    })


class TestGeographicFilters:
    """Test suite for geographic filtering operations."""
    
    @pytest.mark.parametrize("region,expected_count", [
        ('Asia', 2),
        ('Americas', 2),
        ('Europe', 1),
        (None, 5),  # No filter
    ])
    def test_filter_by_region(self, sample_trade_df, region, expected_count):
        """Test filtering by region."""
        result = filter_by_geography(sample_trade_df, region=region)
        assert len(result) == expected_count
    
    @pytest.mark.parametrize("region,subregion,expected_count", [
        ('Asia', 'Eastern Asia', 2),
        ('Asia', 'Western Asia', 0),
        ('Americas', 'Northern America', 1),
        ('Americas', 'South America', 1),
        (None, None, 5),  # No filter
    ])
    def test_filter_by_region_and_subregion(self, sample_trade_df, region, subregion, expected_count):
        """Test cascading region and subregion filters."""
        result = filter_by_geography(sample_trade_df, region=region, subregion=subregion)
        assert len(result) == expected_count
    
    def test_filter_by_country(self, sample_trade_df):
        """Test filtering by specific country."""
        result = filter_by_geography(sample_trade_df, country='China')
        assert len(result) == 2
        assert all(result['exporter_name'] == 'China')


class TestAvailableOptions:
    """Test suite for getting available filter options."""
    
    def test_get_available_subregions_no_filter(self, sample_geo_data):
        """Test getting all subregions when no region filter applied."""
        result = get_available_subregions(sample_geo_data)
        assert len(result) == 5
        assert 'Eastern Asia' in result
        assert 'Western Asia' in result
    
    def test_get_available_subregions_with_region(self, sample_geo_data):
        """Test getting subregions filtered by region."""
        result = get_available_subregions(sample_geo_data, region='Asia')
        assert len(result) == 2
        assert 'Eastern Asia' in result
        assert 'Western Asia' in result
        assert 'Northern America' not in result
    
    def test_get_available_countries_no_filter(self, sample_geo_data):
        """Test getting all countries when no filter applied."""
        result = get_available_countries(sample_geo_data)
        assert len(result) == 5
        assert 'China' in result
        assert 'Türkiye' in result
    
    @pytest.mark.parametrize("region,subregion,expected_countries", [
        ('Asia', None, ['China', 'Türkiye']),
        ('Americas', None, ['USA', 'Brazil']),
        ('Asia', 'Eastern Asia', ['China']),
        ('Asia', 'Western Asia', ['Türkiye']),
    ])
    def test_get_available_countries_with_filters(self, sample_geo_data, region, subregion, expected_countries):
        """Test getting countries filtered by region/subregion."""
        result = get_available_countries(sample_geo_data, region=region, subregion=subregion)
        assert len(result) == len(expected_countries)
        for country in expected_countries:
            assert country in result

