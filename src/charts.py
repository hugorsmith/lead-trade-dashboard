"""Chart styling functions for the Lead Trade Dashboard.

These functions are framework-agnostic (no Streamlit dependencies) to support
future migration to Dash or other frameworks.
"""

import plotly.graph_objects as go
from typing import Literal, Optional


def get_plotly_template(theme: Literal["dark", "light"] = "dark") -> str:
    """
    Get appropriate Plotly template based on theme.

    Args:
        theme: 'dark' or 'light'

    Returns:
        Plotly template name
    """
    return 'plotly' if theme == 'light' else 'plotly_dark'


def get_theme_colors(theme: Literal["dark", "light"] = "dark") -> dict:
    """
    Get color values for the given theme.

    Args:
        theme: 'dark' or 'light'

    Returns:
        Dict with font_color, grid_color, line_color
    """
    if theme == 'light':
        return {
            'font_color': '#1a1a1a',  # Near-black for light theme
            'grid_color': 'rgba(128,128,128,0.1)',
            'line_color': 'rgba(128,128,128,0.2)',
        }
    else:
        return {
            'font_color': '#ffffff',  # White for dark theme
            'grid_color': 'rgba(128,128,128,0.1)',
            'line_color': 'rgba(128,128,128,0.2)',
        }


def apply_chart_theme(
    fig: go.Figure,
    title: str,
    theme: Literal["dark", "light"] = "dark",
    height: int = 550,
    legend_position: Literal["bottom", "top", "none"] = "bottom",
    margin: Optional[dict] = None,
    y_axis_title: Optional[str] = None,
    x_axis_title: Optional[str] = None,
    x_tick_angle: Optional[int] = None,
) -> go.Figure:
    """
    Apply consistent theme styling to a Plotly figure.

    This centralizes all the repeated styling code from app.py into a single
    function. Charts are created in app.py with their data, then this function
    applies the visual styling.

    Args:
        fig: Plotly figure to style
        title: Chart title text
        theme: 'dark' or 'light'
        height: Chart height in pixels
        legend_position: 'bottom', 'top', or 'none'
        margin: Custom margin dict (defaults to standard margins)
        y_axis_title: Optional Y-axis label
        x_axis_title: Optional X-axis label
        x_tick_angle: Optional rotation angle for x-axis tick labels

    Returns:
        The styled figure (modified in place, but also returned for chaining)
    """
    colors = get_theme_colors(theme)

    # Default margin with space for bottom legend
    if margin is None:
        margin = dict(b=120, l=50, r=50, t=50)

    # Legend configuration based on position
    if legend_position == "bottom":
        legend_config = dict(
            orientation="h",
            yanchor="bottom",
            y=-0.55,
            xanchor="center",
            x=0.5
        )
    elif legend_position == "top":
        legend_config = dict(
            title="",
            orientation="h",
            y=1.1,
            x=0
        )
    else:  # none
        legend_config = dict(visible=False)

    # X-axis configuration
    xaxis_config = dict(
        gridcolor=colors['grid_color'],
        linecolor=colors['line_color'],
    )
    if x_axis_title:
        xaxis_config['title'] = x_axis_title
    if x_tick_angle is not None:
        xaxis_config['tickangle'] = x_tick_angle
        xaxis_config['tickfont'] = dict(size=9)
        xaxis_config['automargin'] = True

    # Y-axis configuration
    yaxis_config = dict(
        gridcolor=colors['grid_color'],
        linecolor=colors['line_color'],
    )
    if y_axis_title:
        yaxis_config['title'] = y_axis_title

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['font_color'], size=12),
        title=dict(
            text=title,
            font=dict(color=colors['font_color'], size=16)
        ),
        legend=legend_config,
        xaxis=xaxis_config,
        yaxis=yaxis_config,
        margin=margin,
        height=height,
    )

    return fig


def apply_subplot_theme(
    fig: go.Figure,
    title: str,
    theme: Literal["dark", "light"] = "dark",
    height: int = 400,
    years: Optional[list] = None,
    y1_title: str = "Exports (tons)",
    y2_title: str = "Imports (tons)",
    y2_max: float = 0,
) -> go.Figure:
    """
    Apply theme styling to a 2-row subplot figure (exports/imports).

    This handles the special case of the trade balance chart which has
    two subplots sharing an x-axis.

    Args:
        fig: Plotly subplot figure
        title: Chart title
        theme: 'dark' or 'light'
        height: Chart height in pixels
        years: List of year values for x-axis ticks
        y1_title: Title for top subplot y-axis
        y2_title: Title for bottom subplot y-axis
        y2_max: Max value for inverted y2 axis range

    Returns:
        The styled figure
    """
    colors = get_theme_colors(theme)

    layout_updates = dict(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            title="",
            orientation="h",
            y=1.1,
            x=0
        ),
        font=dict(color=colors['font_color'], size=12),
        title=dict(
            text=title,
            font=dict(color=colors['font_color'], size=16)
        ),
        barmode="stack",
        template=get_plotly_template(theme),
        margin=dict(b=30, l=50, r=50, t=60),
        height=height,
    )

    # X-axis 1 (top subplot)
    xaxis1 = dict(
        gridcolor=colors['grid_color'],
        linecolor=colors['line_color'],
        title="",
        domain=[0, 1]
    )
    if years is not None:
        xaxis1['tickvals'] = years
        xaxis1['ticktext'] = [str(y) for y in years]

    # X-axis 2 (bottom subplot)
    xaxis2 = dict(
        gridcolor=colors['grid_color'],
        linecolor=colors['line_color'],
        title="",
        domain=[0, 1],
        showticklabels=False
    )
    if years is not None:
        xaxis2['tickvals'] = years
        xaxis2['ticktext'] = [str(y) for y in years]

    layout_updates['xaxis'] = xaxis1
    layout_updates['xaxis2'] = xaxis2

    # Y-axes
    layout_updates['yaxis'] = dict(
        gridcolor=colors['grid_color'],
        linecolor=colors['line_color'],
        title=y1_title,
    )
    layout_updates['yaxis2'] = dict(
        gridcolor=colors['grid_color'],
        linecolor=colors['line_color'],
        title=y2_title,
        range=[y2_max, 0]  # Inverted for imports
    )

    fig.update_layout(**layout_updates)

    return fig


def apply_choropleth_theme(
    fig: go.Figure,
    title: str,
    theme: Literal["dark", "light"] = "dark",
    height: int = 450,
) -> go.Figure:
    """
    Apply theme styling to a choropleth map.

    Args:
        fig: Plotly choropleth figure
        title: Chart title
        theme: 'dark' or 'light'
        height: Chart height in pixels

    Returns:
        Styled figure
    """
    colors = get_theme_colors(theme)

    # Geo styling based on theme
    if theme == 'light':
        geo_bgcolor = 'rgba(0,0,0,0)'
        land_color = '#f0f0f0'
        ocean_color = '#e6f2ff'
        border_color = '#999999'
    else:
        geo_bgcolor = 'rgba(0,0,0,0)'
        land_color = '#2d2d2d'
        ocean_color = '#1a1a2e'
        border_color = '#444444'

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(color=colors['font_color'], size=16),
            x=0.5,
            xanchor='center'
        ),
        font=dict(color=colors['font_color'], size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=height,
        margin=dict(l=0, r=0, t=50, b=0),
        geo=dict(
            bgcolor=geo_bgcolor,
            landcolor=land_color,
            oceancolor=ocean_color,
            showocean=False,
            showlakes=False,
            showland=False,
            showcountries=True,
            countrycolor=border_color,
            countrywidth=0.5,
            projection_type='equirectangular',
        ),
        coloraxis_colorbar=dict(
            title=dict(text='Net Trade (tons)', font=dict(color=colors['font_color'])),
            tickfont=dict(color=colors['font_color']),
        )
    )

    return fig
