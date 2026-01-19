"""Filter functions for trade data."""

import pandas as pd
from typing import Optional, List


def filter_by_geography(
    df: pd.DataFrame,
    region: Optional[str] = None,
    subregion: Optional[str] = None,
    intermediate_region: Optional[str] = None,
    country: Optional[str] = None
) -> pd.DataFrame:
    """
    Apply cascading geographic filters (region > subregion > intermediate_region > country).
    
    Args:
        df: DataFrame with 'region', 'subregion', 'intermediate_region', and country columns
        region: Region to filter by (optional)
        subregion: Subregion to filter by (optional)
        intermediate_region: Intermediate region to filter by (optional)
        country: Country name to filter by (optional)
        
    Returns:
        Filtered DataFrame
    """
    filtered = df.copy()
    
    if country is not None:
        # If country is specified, filter by it (most specific)
        filtered = filtered[filtered['exporter_name'] == country]
    else:
        # Otherwise apply cascading region/subregion/intermediate_region filters
        if region is not None:
            filtered = filtered[filtered['region'] == region]
        if subregion is not None:
            filtered = filtered[filtered['subregion'] == subregion]
        if intermediate_region is not None:
            filtered = filtered[filtered['intermediate_region'] == intermediate_region]
    
    return filtered


def get_available_subregions(
    df: pd.DataFrame,
    region: Optional[str] = None
) -> List[str]:
    """
    Get list of available subregions, optionally filtered by region.
    
    Args:
        df: DataFrame with 'region' and 'subregion' columns
        region: Region to filter by (optional)
        
    Returns:
        Sorted list of unique subregions
    """
    filtered = df[df['subregion'].notna()]
    
    if region is not None:
        filtered = filtered[filtered['region'] == region]
    
    return sorted(filtered['subregion'].drop_duplicates().to_list())


def get_available_intermediate_regions(
    df: pd.DataFrame,
    region: Optional[str] = None,
    subregion: Optional[str] = None
) -> List[str]:
    """
    Get list of available intermediate regions, optionally filtered by region/subregion.
    
    Args:
        df: DataFrame with 'region', 'subregion', and 'intermediate_region' columns
        region: Region to filter by (optional)
        subregion: Subregion to filter by (optional)
        
    Returns:
        Sorted list of unique intermediate regions
    """
    filtered = df[df['intermediate_region'].notna()]
    
    if region is not None:
        filtered = filtered[filtered['region'] == region]
    if subregion is not None:
        filtered = filtered[filtered['subregion'] == subregion]
    
    return sorted(filtered['intermediate_region'].drop_duplicates().to_list())


def get_available_countries(
    df: pd.DataFrame,
    region: Optional[str] = None,
    subregion: Optional[str] = None,
    intermediate_region: Optional[str] = None
) -> List[str]:
    """
    Get list of available countries, optionally filtered by region/subregion/intermediate_region.
    
    Args:
        df: DataFrame with 'region', 'subregion', 'intermediate_region', and 'name' columns
        region: Region to filter by (optional)
        subregion: Subregion to filter by (optional)
        intermediate_region: Intermediate region to filter by (optional)
        
    Returns:
        Sorted list of unique country names
    """
    filtered = df[df['name'].notna()]
    
    if region is not None:
        filtered = filtered[filtered['region'] == region]
    if subregion is not None:
        filtered = filtered[filtered['subregion'] == subregion]
    if intermediate_region is not None:
        filtered = filtered[filtered['intermediate_region'] == intermediate_region]
    
    return sorted(filtered['name'].drop_duplicates().to_list())

