// Chart theming — a direct port of src/charts.py.
//
// One deliberate difference: plotly.py resolved named templates ("plotly_dark",
// "plotly") server-side and inlined the entire template object into the figure
// JSON it sent us. plotly.js ships no named templates, so passing
// `template: 'plotly_dark'` here would silently do nothing. Instead we set the
// handful of layout properties the template actually contributed — transparent
// backgrounds plus font/grid/line colours — which is what made the charts look
// themed in the first place.

export function getThemeColors(theme = 'dark') {
  // Both themes share grid/line colours; only the font colour differs.
  return {
    font: theme === 'light' ? '#1a1a1a' : '#ffffff',
    grid: 'rgba(128,128,128,0.1)',
    line: 'rgba(128,128,128,0.2)',
  }
}

function legendConfig(position) {
  if (position === 'bottom') {
    return { orientation: 'h', yanchor: 'bottom', y: -0.55, xanchor: 'center', x: 0.5 }
  }
  if (position === 'top') {
    return { title: { text: '' }, orientation: 'h', y: 1.1, x: 0 }
  }
  return { visible: false }
}

/** Standard single-plot layout (src/charts.py: apply_chart_theme). */
export function chartLayout({
  title = '',
  theme = 'dark',
  height = 550,
  legendPosition = 'bottom',
  margin = { b: 120, l: 50, r: 50, t: 50 },
  yAxisTitle = null,
  xAxisTitle = null,
  xTickAngle = null,
} = {}) {
  const c = getThemeColors(theme)

  const xaxis = { gridcolor: c.grid, linecolor: c.line }
  if (xAxisTitle) xaxis.title = { text: xAxisTitle }
  if (xTickAngle != null) {
    xaxis.tickangle = xTickAngle
    xaxis.tickfont = { size: 9 }
    xaxis.automargin = true
  }

  const yaxis = { gridcolor: c.grid, linecolor: c.line }
  if (yAxisTitle) yaxis.title = { text: yAxisTitle }

  return {
    plot_bgcolor: 'rgba(0,0,0,0)',
    paper_bgcolor: 'rgba(0,0,0,0)',
    font: { color: c.font, size: 12 },
    title: { text: title, font: { color: c.font, size: 16 } },
    legend: legendConfig(legendPosition),
    xaxis,
    yaxis,
    margin,
    height,
  }
}

/**
 * Two-row exports/imports subplot layout (src/charts.py: apply_subplot_theme).
 * The bottom axis range is inverted so imports mirror downward.
 */
export function subplotLayout({
  title = '',
  theme = 'dark',
  height = 400,
  years = null,
  y1Title = 'Exports (tons)',
  y2Title = 'Imports (tons)',
  y2Max = 0,
} = {}) {
  const c = getThemeColors(theme)

  const axis = (showTicks) => {
    const a = { gridcolor: c.grid, linecolor: c.line, title: { text: '' }, domain: [0, 1] }
    if (years) {
      a.tickvals = years
      a.ticktext = years.map(String)
    }
    if (!showTicks) a.showticklabels = false
    return a
  }

  return {
    plot_bgcolor: 'rgba(0,0,0,0)',
    paper_bgcolor: 'rgba(0,0,0,0)',
    legend: { title: { text: '' }, orientation: 'h', y: 1.1, x: 0 },
    font: { color: c.font, size: 12 },
    title: { text: title, font: { color: c.font, size: 16 } },
    barmode: 'stack',
    margin: { b: 30, l: 50, r: 50, t: 60 },
    height,
    xaxis: axis(true),
    xaxis2: axis(false),
    yaxis: { gridcolor: c.grid, linecolor: c.line, title: { text: y1Title }, domain: [0.575, 1] },
    yaxis2: {
      gridcolor: c.grid,
      linecolor: c.line,
      title: { text: y2Title },
      range: [y2Max, 0], // inverted for imports
      domain: [0, 0.425],
    },
  }
}

/** Choropleth map layout (src/charts.py: apply_choropleth_theme). */
export function choroplethLayout({ title = '', theme = 'dark', height = 450 } = {}) {
  const c = getThemeColors(theme)
  const light = theme === 'light'

  return {
    title: { text: title, font: { color: c.font, size: 16 }, x: 0.5, xanchor: 'center' },
    font: { color: c.font, size: 12 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    height,
    margin: { l: 0, r: 0, t: 50, b: 0 },
    geo: {
      bgcolor: 'rgba(0,0,0,0)',
      landcolor: light ? '#f0f0f0' : '#2d2d2d',
      oceancolor: light ? '#e6f2ff' : '#1a1a2e',
      showocean: false,
      showlakes: false,
      showland: false,
      showcountries: true,
      countrycolor: light ? '#999999' : '#444444',
      countrywidth: 0.5,
      projection: { type: 'equirectangular' },
    },
  }
}
