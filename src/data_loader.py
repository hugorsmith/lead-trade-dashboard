"""Data loading and processing functions."""

import pandas as pd
from .config import HS_TO_CATEGORY


def load_trade_data(filepath: str = 'lead_trade_data.csv') -> pd.DataFrame:
    """
    Load and process trade data from CSV.
    
    Processing steps:
    1. Load CSV with UTF-8 encoding
    2. Fix encoding issues (TÃ¼rkiye → Türkiye)
    3. Pad product codes to 6 digits
    4. Assign product categories
    
    Args:
        filepath: Path to the trade data CSV file
        
    Returns:
        Processed trade data DataFrame
        
    Raises:
        Exception: If file cannot be loaded
    """
    try:
        df = pd.read_csv(filepath, encoding='utf-8')
        
        # Fix encoding issues
        df['exporter_name'] = df['exporter_name'].str.replace('TÃ¼rkiye', 'Türkiye', regex=False)
        df['importer_name'] = df['importer_name'].str.replace('TÃ¼rkiye', 'Türkiye', regex=False)
        
        # Pad product codes to 6 digits
        df['product'] = df['product'].astype(str).str.zfill(6)
        
        # Assign categories
        df['category'] = df['product'].map(HS_TO_CATEGORY)
        
        return df
    except Exception as e:
        raise Exception(f"Error loading trade data: {str(e)}")


def load_country_data(filepath: str = 'countries.csv') -> pd.DataFrame:
    """
    Load country metadata from CSV.
    
    Args:
        filepath: Path to the countries CSV file
        
    Returns:
        Country metadata DataFrame
        
    Raises:
        Exception: If file cannot be loaded
    """
    try:
        df = pd.read_csv(filepath, encoding='utf-8')
        return df
    except Exception as e:
        raise Exception(f"Error loading country data: {str(e)}")

