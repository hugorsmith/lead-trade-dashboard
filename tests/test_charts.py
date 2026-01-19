"""
Tests for chart styling functions.
"""
import pytest
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.charts import (
    get_plotly_template,
    get_theme_colors,
    apply_chart_theme,
    apply_subplot_theme,
)


class TestPlotlyTemplate:
    """Test suite for Plotly template selection."""

    @pytest.mark.parametrize("theme,expected", [
        ("dark", "plotly_dark"),
        ("light", "plotly"),
    ])
    def test_get_plotly_template(self, theme, expected):
        """Test that correct Plotly template is returned for theme."""
        result = get_plotly_template(theme)
        assert result == expected


class TestThemeColors:
    """Test suite for theme color configuration."""

    def test_dark_theme_returns_white_font(self):
        """Test that dark theme returns white font color."""
        colors = get_theme_colors("dark")
        assert colors['font_color'] == '#ffffff'

    def test_light_theme_returns_dark_font(self):
        """Test that light theme returns near-black font color."""
        colors = get_theme_colors("light")
        assert colors['font_color'] == '#1a1a1a'

    def test_colors_include_grid_and_line(self):
        """Test that color dict includes grid and line colors."""
        colors = get_theme_colors("dark")
        assert 'grid_color' in colors
        assert 'line_color' in colors


class TestApplyChartTheme:
    """Test suite for apply_chart_theme function."""

    def test_returns_figure(self):
        """Test that apply_chart_theme returns a Plotly figure."""
        fig = go.Figure()
        result = apply_chart_theme(fig, "Test Chart", "dark")
        assert isinstance(result, go.Figure)

    def test_adds_title(self):
        """Test that chart title is applied."""
        fig = go.Figure()
        result = apply_chart_theme(fig, "Test Title", "dark")
        assert result.layout.title.text == "Test Title"

    def test_sets_height(self):
        """Test that chart height is set."""
        fig = go.Figure()
        result = apply_chart_theme(fig, "Test", "dark", height=600)
        assert result.layout.height == 600

    def test_default_height_is_550(self):
        """Test that default height is 550."""
        fig = go.Figure()
        result = apply_chart_theme(fig, "Test", "dark")
        assert result.layout.height == 550

    @pytest.mark.parametrize("theme", ["dark", "light"])
    def test_applies_transparent_background(self, theme):
        """Test that background is transparent for both themes."""
        fig = go.Figure()
        result = apply_chart_theme(fig, "Test", theme)
        assert result.layout.plot_bgcolor == 'rgba(0,0,0,0)'
        assert result.layout.paper_bgcolor == 'rgba(0,0,0,0)'

    def test_bottom_legend_position(self):
        """Test that bottom legend is positioned correctly."""
        fig = go.Figure()
        result = apply_chart_theme(fig, "Test", "dark", legend_position="bottom")
        assert result.layout.legend.orientation == "h"
        assert result.layout.legend.y == -0.55

    def test_top_legend_position(self):
        """Test that top legend is positioned correctly."""
        fig = go.Figure()
        result = apply_chart_theme(fig, "Test", "dark", legend_position="top")
        assert result.layout.legend.orientation == "h"
        assert result.layout.legend.y == 1.1

    def test_x_tick_angle(self):
        """Test that x_tick_angle is applied."""
        fig = go.Figure()
        result = apply_chart_theme(fig, "Test", "dark", x_tick_angle=30)
        assert result.layout.xaxis.tickangle == 30
        assert result.layout.xaxis.automargin is True


class TestApplySubplotTheme:
    """Test suite for apply_subplot_theme function (trade balance chart)."""

    @pytest.fixture
    def subplot_fig(self):
        """Create a basic 2-row subplot figure."""
        return make_subplots(rows=2, cols=1)

    def test_returns_figure(self, subplot_fig):
        """Test that apply_subplot_theme returns a Plotly figure."""
        result = apply_subplot_theme(subplot_fig, "Test Chart", "dark")
        assert isinstance(result, go.Figure)

    def test_adds_title(self, subplot_fig):
        """Test that chart title is applied."""
        result = apply_subplot_theme(subplot_fig, "My Title", "dark")
        assert result.layout.title.text == "My Title"

    def test_sets_barmode_stack(self, subplot_fig):
        """Test that barmode is set to stack."""
        result = apply_subplot_theme(subplot_fig, "Test", "dark")
        assert result.layout.barmode == "stack"

    def test_default_height_is_400(self, subplot_fig):
        """Test that default height is 400 for subplot chart."""
        result = apply_subplot_theme(subplot_fig, "Test", "dark")
        assert result.layout.height == 400

    def test_y2_axis_inverted(self, subplot_fig):
        """Test that y2 axis (imports) is inverted."""
        result = apply_subplot_theme(subplot_fig, "Test", "dark", y2_max=1000)
        assert list(result.layout.yaxis2.range) == [1000, 0]

    def test_years_set_as_tickvals(self, subplot_fig):
        """Test that years are set as tick values."""
        years = [2020, 2021, 2022]
        result = apply_subplot_theme(subplot_fig, "Test", "dark", years=years)
        assert list(result.layout.xaxis.tickvals) == years

    def test_applies_template(self, subplot_fig):
        """Test that plotly template is applied."""
        result = apply_subplot_theme(subplot_fig, "Test", "dark")
        assert result.layout.template.layout.paper_bgcolor is not None

    @pytest.mark.parametrize("theme", ["dark", "light"])
    def test_both_themes_work(self, subplot_fig, theme):
        """Test that both themes are supported."""
        result = apply_subplot_theme(subplot_fig, "Test", theme)
        assert result is not None
