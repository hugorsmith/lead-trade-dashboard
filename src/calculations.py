"""Calculation functions for trade metrics."""


def calculate_yoy_change(current_value: float, previous_value: float) -> float:
    """
    Calculate year-over-year percentage change.
    
    Args:
        current_value: Value for current period
        previous_value: Value for previous period
        
    Returns:
        Percentage change (e.g., 20.0 for 20% growth)
        Returns 0 if previous_value is 0 (to avoid division by zero)
    """
    if previous_value == 0:
        return 0
    return ((current_value - previous_value) / previous_value) * 100
