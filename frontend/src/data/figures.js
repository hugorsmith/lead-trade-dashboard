// Plotly figure builders — the port of backend/figures.py.
//
// Each returns a plain {data, layout} object for react-plotly.js, replacing the
// figures the server used to build with plotly.py and ship as JSON.
//
// One deliberate improvement over the original: plotly.express assigned colours
// positionally, handing the Nth *distinct product present in the data* the Nth
// entry of `color_discrete_sequence`. When a selected product had no rows for a
// selection, every subsequent product silently shifted to the wrong colour.
// Here each trace carries its own product's colour by lookup, so a product is
// always drawn in its configured colour.

import { chartLayout, subplotLayout, choroplethLayout } from './theme.js'

/** fig0 — two-row exports (top) / imports (bottom, inverted) by category. */
export function buildCategoryTradeFigure(categoryTrade, productIndex, theme = 'dark') {
  const { byCategory, years } = categoryTrade
  const data = []
  let y2Max = 0

  // Config order (raw ore -> refined -> products -> waste) rather than the
  // alphabetical order the server's pivot happened to produce.
  for (const category of productIndex.categories) {
    const rows = byCategory.get(category)
    if (!rows) continue

    const color = productIndex.categoryColor[category]
    const exports = years.map((y) => rows.get(y)?.exports ?? 0)
    const imports = years.map((y) => rows.get(y)?.imports ?? 0)
    y2Max = Math.max(y2Max, ...imports)

    data.push({
      type: 'bar', x: years, y: exports, name: category,
      marker: { color }, xaxis: 'x', yaxis: 'y',
      hovertemplate: `%{x}<br>${category}: %{y:,.0f} tons<extra></extra>`,
    })
    data.push({
      type: 'bar', x: years, y: imports, name: category, showlegend: false,
      marker: { color }, xaxis: 'x2', yaxis: 'y2',
      hovertemplate: `%{x}<br>${category}: %{y:,.0f} tons<extra></extra>`,
    })
  }

  return { data, layout: subplotLayout({ theme, years, y2Max }) }
}

/** fig1 / fig3 — stacked volume-by-HS-code bars over years. */
export function buildHsBarFigure(agg, selectedCodes, productIndex, theme = 'dark') {
  const { byProduct, years } = agg
  const data = []

  for (const code of productIndex.allCodes) {
    if (!selectedCodes.includes(code)) continue
    const rows = byProduct.get(productIndex.order[code])
    if (!rows) continue

    data.push({
      type: 'bar',
      x: years,
      y: years.map((y) => rows.get(y) ?? 0),
      name: productIndex.labels[code],
      marker: { color: productIndex.colors[code] },
      hovertemplate: '%{x}<br>%{y:,.0f} tons<extra></extra>',
    })
  }

  const layout = chartLayout({ theme })
  layout.barmode = 'stack'
  layout.xaxis.title = { text: 'Year' }
  layout.yaxis.title = { text: 'Volume (tons)' }
  layout.legend.title = { text: 'HS Code' }
  return { data, layout }
}

/** fig2 / fig4 — top-20 destinations/sources, stacked by HS code. */
export function buildTopPartnersFigure(top, partnerCol, store, selectedCodes, productIndex, theme = 'dark') {
  const { order, byPartner } = top
  const names = order.map((p) => store.nameOf(p))
  const data = []

  for (const code of productIndex.allCodes) {
    if (!selectedCodes.includes(code)) continue
    const i = productIndex.order[code]
    if (!order.some((p) => byPartner.get(p)?.has(i))) continue

    data.push({
      type: 'bar',
      x: names,
      y: order.map((p) => byPartner.get(p)?.get(i) ?? 0),
      name: productIndex.labels[code],
      marker: { color: productIndex.colors[code] },
      hovertemplate: '%{x}<br>%{y:,.0f} tons<extra></extra>',
    })
  }

  const layout = chartLayout({ theme, xTickAngle: 30 })
  layout.barmode = 'stack'
  layout.xaxis.title = { text: partnerCol === 'importer' ? 'Importing Country' : 'Exporting Country' }
  layout.xaxis.categoryorder = 'array'
  layout.xaxis.categoryarray = names
  layout.yaxis.title = { text: 'Volume (tons)' }
  layout.legend.title = { text: 'HS Code' }
  return { data, layout }
}

/**
 * Safety-of-source bars: coloured by whether the source country is flagged for
 * unsafe used-lead-acid-battery recycling, rather than stacked by HS code.
 */
export function buildSafetyFigure(totals, store, flagged, flagColor, theme = 'dark') {
  const neutral = theme === 'dark' ? '#94a3b8' : '#64748b'
  const names = totals.map((t) => store.nameOf(t.partner))

  const data = [{
    type: 'bar',
    x: names,
    y: totals.map((t) => t.quantity),
    marker: { color: names.map((n) => (flagged.has(n) ? flagColor : neutral)) },
    hovertemplate: '%{x}<br>%{y:,.0f} tons<extra></extra>',
  }]

  const layout = chartLayout({
    theme,
    legendPosition: 'none',
    xAxisTitle: 'Exporting Country',
    yAxisTitle: 'Volume (tons)',
    xTickAngle: 30,
  })
  layout.xaxis.tickmode = 'array'
  layout.xaxis.tickvals = names
  layout.xaxis.ticktext = names.map((n) =>
    flagged.has(n) ? `<span style="color:${flagColor}">${n}</span>` : n
  )
  return { data, layout }
}

/** Choropleth of net trade (exports - imports) per partner. Null when empty. */
export function buildMapFigure(mapData, store, title, theme = 'dark') {
  if (!mapData.length) return null

  const maxAbs = Math.max(
    1,
    ...mapData.map((r) => Math.abs(r.net_trade)),
  )

  const data = [{
    type: 'choropleth',
    locationmode: 'ISO-3',
    locations: mapData.map((r) => store.iso[r.partner]),
    z: mapData.map((r) => r.net_trade),
    text: mapData.map((r) => store.nameOf(r.partner)),
    customdata: mapData.map((r) => [r.exports, r.imports]),
    colorscale: [
      [0, '#1b7837'],   // dark green — net importer from the selection
      [0.5, '#f7f7f7'], // neutral
      [1, '#762a83'],   // purple — net exporter to the selection
    ],
    zmin: -maxAbs,
    zmax: maxAbs,
    marker: { line: { width: 0 } },
    colorbar: {
      title: { text: 'Net Trade (tons)' },
    },
    hovertemplate:
      '<b>%{text}</b><br>Exports: %{customdata[0]:,.0f}<br>' +
      'Imports: %{customdata[1]:,.0f}<br>Net Trade: %{z:,.0f}<extra></extra>',
  }]

  return { data, layout: choroplethLayout({ title, theme }) }
}
