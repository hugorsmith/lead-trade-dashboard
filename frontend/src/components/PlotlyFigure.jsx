import createPlotlyComponent from 'react-plotly.js/factory'
import Plotly from 'plotly.js-dist-min'

const Plot = createPlotlyComponent(Plotly)

// Renders a Plotly figure produced by the backend (fig.to_json() -> {data, layout}).
// The backend already applies all theming, so we only set sizing/config here.
export default function PlotlyFigure({ figure, height }) {
  if (!figure) return <div className="chart-empty">No data for the current selection.</div>

  const layout = {
    ...figure.layout,
    autosize: true,
    ...(height ? { height } : {}),
  }

  return (
    <Plot
      data={figure.data}
      layout={layout}
      config={{ displayModeBar: false, responsive: true }}
      useResizeHandler
      style={{ width: '100%', height: height ? `${height}px` : '100%' }}
    />
  )
}
