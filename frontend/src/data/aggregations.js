// Aggregations — a direct port of src/aggregations.py, running in the browser.
//
// Each function takes the columnar `store` (see store.js) plus a list of row
// indices for one side of a selection, mirroring the pandas frames the server
// used to pass around:
//   * `exportIdx` = rows where the selection is the exporter (outbound trade)
//   * `importIdx` = rows where the selection is the importer (inbound trade)
//
// Partners are carried as ISO-3 *indices* internally and only resolved to
// display names at the edge, which is both faster and immune to the
// name-matching fragility the server-side version had.
//
// Grouped results are returned as nested Maps rather than Maps keyed by a
// joined string: the group keys are integers (product index, year, ISO index),
// so nesting avoids inventing a separator that producer and consumer have to
// agree on byte-for-byte.

/** Accumulate `delta` into a two-level Map. */
function bump(outer, k1, k2, delta) {
  let inner = outer.get(k1)
  if (!inner) outer.set(k1, (inner = new Map()))
  inner.set(k2, (inner.get(k2) ?? 0) + delta)
}

/** Year-over-year % change; 0 when the previous value is 0 (src/calculations.py). */
export function calculateYoyChange(current, previous) {
  if (previous === 0) return 0
  return ((current - previous) / previous) * 100
}

/**
 * The four headline KPIs with YoY deltas (aggregations.py: compute_kpis).
 * Partner count is the union of destinations and sources in `metricsYear`.
 */
export function computeKpis(store, exportIdx, importIdx, metricsYear) {
  const { year, quantity, importer, exporter } = store

  let totalExports = 0
  let exportsPrev = 0
  const partners = new Set()

  for (const i of exportIdx) {
    if (year[i] === metricsYear) {
      totalExports += quantity[i]
      partners.add(importer[i])
    } else if (year[i] === metricsYear - 1) {
      exportsPrev += quantity[i]
    }
  }

  let totalImports = 0
  let importsPrev = 0
  for (const i of importIdx) {
    if (year[i] === metricsYear) {
      totalImports += quantity[i]
      partners.add(exporter[i])
    } else if (year[i] === metricsYear - 1) {
      importsPrev += quantity[i]
    }
  }

  return {
    total_exports: totalExports,
    total_imports: totalImports,
    export_change: calculateYoyChange(totalExports, exportsPrev),
    import_change: calculateYoyChange(totalImports, importsPrev),
    trade_balance: totalExports - totalImports,
    num_partners: partners.size,
    metrics_year: metricsYear,
  }
}

/**
 * Quantity by (product, year) for the stacked HS-code bar charts
 * (aggregations.py: aggregate_by_hs_year).
 *
 * @returns {{ byProduct: Map<number, Map<number, number>>, years: number[] }}
 *   product index -> year -> quantity, plus the ascending year list.
 */
export function aggregateByHsYear(store, idx) {
  const { year, product, quantity } = store
  const byProduct = new Map()
  const years = new Set()

  for (const i of idx) {
    years.add(year[i])
    bump(byProduct, product[i], year[i], quantity[i])
  }

  return { byProduct, years: [...years].sort((a, b) => a - b) }
}

/**
 * Exports vs imports per (category, year) for the two-row subplot
 * (aggregations.py: aggregate_category_trade). Missing sides are 0.
 *
 * @returns {{ byCategory: Map<string, Map<number, {exports:number, imports:number}>>,
 *             years: number[] }}
 */
export function aggregateCategoryTrade(store, exportIdx, importIdx, productIndex) {
  const { year, product, quantity, productCodes } = store
  const byCategory = new Map()
  const years = new Set()

  const add = (idx, field) => {
    for (const i of idx) {
      const category = productIndex.toCategory[productCodes[product[i]]]
      const y = year[i]
      years.add(y)

      let inner = byCategory.get(category)
      if (!inner) byCategory.set(category, (inner = new Map()))
      let row = inner.get(y)
      if (!row) inner.set(y, (row = { exports: 0, imports: 0 }))
      row[field] += quantity[i]
    }
  }

  add(exportIdx, 'exports')
  add(importIdx, 'imports')

  return { byCategory, years: [...years].sort((a, b) => a - b) }
}

/**
 * Top-N partners for a year with a per-HS-code breakdown
 * (aggregations.py: top_partners).
 *
 * @param partnerCol 'importer' (export destinations) or 'exporter' (import sources)
 * @returns {{ order: number[], byPartner: Map<number, Map<number, number>> }}
 *   partner ISO indices in descending total volume, and partner -> product -> quantity.
 */
export function topPartners(store, idx, partnerCol, year, n = 20) {
  const partnerCode = store[partnerCol]
  const { year: yearCol, product, quantity } = store

  const totals = new Map()
  const byPartner = new Map()

  for (const i of idx) {
    if (yearCol[i] !== year) continue
    const p = partnerCode[i]
    totals.set(p, (totals.get(p) ?? 0) + quantity[i])
    bump(byPartner, p, product[i], quantity[i])
  }

  const order = [...totals.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, n)
    .map(([p]) => p)

  return { order, byPartner }
}

/**
 * Total quantity per partner for a year, no HS breakdown
 * (aggregations.py: total_by_partner). Used by the safety-of-source view.
 */
export function totalByPartner(store, idx, partnerCol, year, n = 25) {
  const partnerCode = store[partnerCol]
  const { year: yearCol, quantity } = store

  const totals = new Map()
  for (const i of idx) {
    if (yearCol[i] !== year) continue
    const p = partnerCode[i]
    totals.set(p, (totals.get(p) ?? 0) + quantity[i])
  }

  return [...totals.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, n)
    .map(([partner, quantity]) => ({ partner, quantity }))
}

/**
 * Net-trade-by-partner frame for the choropleth (aggregations.py: build_map_data).
 * Outer join of the selection's exports-by-destination and imports-by-source.
 */
export function buildMapData(store, exportIdx, importIdx, mapYear) {
  const { year, quantity, importer, exporter } = store
  const rows = new Map() // partner ISO index -> {partner, exports, imports, net_trade}

  const get = (p) => {
    let row = rows.get(p)
    if (!row) rows.set(p, (row = { partner: p, exports: 0, imports: 0, net_trade: 0 }))
    return row
  }

  for (const i of exportIdx) {
    if (year[i] === mapYear) get(importer[i]).exports += quantity[i]
  }
  for (const i of importIdx) {
    if (year[i] === mapYear) get(exporter[i]).imports += quantity[i]
  }

  const out = [...rows.values()]
  for (const r of out) r.net_trade = r.exports - r.imports
  return out
}
