// Data access + client-side geo cascade.
//
// There is no backend. The browser loads two static assets once
// (data/meta.json + data/trade.tsv, produced by scripts/export_data.py) and
// every KPI and chart series is computed here on demand.
//
// These functions return plain series data, not rendered figures — the chart
// components in charts/ own all the drawing.
//
// The cascade helpers replicate src/filters.py (get_available_subregions /
// _intermediate_regions / _countries) exactly: drop rows where the target
// column is null, apply the upstream filters, then return sorted unique values.

import { loadStore, resolveSelection, buildDownloadCsv } from './data/store.js'
import {
  computeKpis,
  aggregateByHsYear,
  aggregateCategoryTrade,
  topPartners,
  totalByPartner,
} from './data/aggregations.js'
import { FLAG_COLOR, UNSAFE_SOURCES, flaggedCountries } from './data/safety.js'

// --- One-time load --------------------------------------------------------
let _loading = null

/** Load (once) and return the in-browser data store. */
export function ensureStore() {
  if (!_loading) _loading = loadStore()
  return _loading
}

/** Refined lead ("New Lead") HS codes — the fixed scope of the safety view. */
const newLeadCodes = (store) =>
  store.products.allCodes.filter((c) => store.products.toCategory[c] === 'New Lead')

const range = (from, to) =>
  Array.from({ length: Math.max(to - from + 1, 0) }, (_, i) => from + i)

/**
 * One series per selected product, over a fixed year axis.
 * Products with no rows in the selection are dropped so they don't sit in the
 * legend as permanently-empty entries.
 */
function productSeries(store, agg, selectedCodes, years) {
  const p = store.products
  return p.allCodes
    .filter((code) => selectedCodes.includes(code))
    .map((code) => {
      const rows = agg.byProduct.get(p.order[code])
      if (!rows) return null
      return {
        key: code,
        label: p.labels[code],
        short: `${code}`,
        color: p.colors[code],
        values: years.map((y) => rows.get(y) ?? 0),
      }
    })
    .filter(Boolean)
}

// --- "Endpoints" ----------------------------------------------------------

export async function fetchMeta() {
  const store = await ensureStore()
  return store.meta
}

/** KPIs, the per-product volume series, and the category mirror series. */
export async function fetchDashboard(filters) {
  const store = await ensureStore()
  const sel = resolveSelection(store, filters)

  // A fixed year axis across every chart, so gaps read as gaps rather than
  // silently collapsing and misaligning the exports and imports panels.
  const years = range(sel.yearStart, sel.yearEnd)

  const yearlyExports = aggregateByHsYear(store, sel.exportIdx)
  const yearlyImports = aggregateByHsYear(store, sel.importIdx)
  const categoryTrade = aggregateCategoryTrade(store, sel.exportIdx, sel.importIdx, store.products)

  const categorySeries = store.products.categories
    .map((category) => {
      const rows = categoryTrade.byCategory.get(category)
      if (!rows) return null
      return {
        key: category,
        label: category,
        color: store.products.categoryColor[category],
        exports: years.map((y) => rows.get(y)?.exports ?? 0),
        imports: years.map((y) => rows.get(y)?.imports ?? 0),
      }
    })
    .filter(Boolean)

  return {
    label: sel.label,
    metrics_year: sel.metricsYear,
    year_start: sel.yearStart,
    year_end: sel.yearEnd,
    years,
    kpis: computeKpis(store, sel.exportIdx, sel.importIdx, sel.metricsYear),
    export_years: sel.exportYears,
    import_years: sel.importYears,
    exportSeries: productSeries(store, yearlyExports, sel.selectedCodes, years),
    importSeries: productSeries(store, yearlyImports, sel.selectedCodes, years),
    categorySeries,
  }
}

/** Top-20 destinations (exports) or sources (imports) for a chosen year. */
export async function fetchTop(filters) {
  const store = await ensureStore()
  const { direction, year } = filters
  const sel = resolveSelection(store, filters)

  const isExports = direction === 'exports'
  const idx = isExports ? sel.exportIdx : sel.importIdx
  const top = topPartners(store, idx, isExports ? 'importer' : 'exporter', year)

  const partners = top.order.map((p) => store.nameOf(p))
  const p = store.products
  const series = p.allCodes
    .filter((code) => sel.selectedCodes.includes(code))
    .map((code) => {
      const i = p.order[code]
      if (!top.order.some((partner) => top.byPartner.get(partner)?.has(i))) return null
      return {
        key: code,
        label: p.labels[code],
        color: p.colors[code],
        values: top.order.map((partner) => top.byPartner.get(partner)?.get(i) ?? 0),
      }
    })
    .filter(Boolean)

  return { direction, year, partners, series, available_years: isExports ? sel.exportYears : sel.importYears }
}

/** US refined-lead import sources, flagged by unsafe-ULAB-recycling status. */
export async function fetchSafety({ year } = {}) {
  const store = await ensureStore()

  // Fixed scope: imports INTO the USA, refined lead ("New Lead") only.
  const sel = resolveSelection(store, { products: newLeadCodes(store), country: 'USA' })
  const availableYears = sel.importYears
  const selectedYear = year ?? availableYears[0] ?? sel.yearEnd

  const totals = totalByPartner(store, sel.importIdx, 'exporter', selectedYear, 25)
  const sources = totals.map((t) => ({ name: store.nameOf(t.partner), value: t.quantity }))
  const present = new Set(sources.map((s) => s.name))

  return {
    year: selectedYear,
    available_years: availableYears,
    flagColor: FLAG_COLOR,
    flagged: Object.entries(UNSAFE_SOURCES).map(([country, citations]) => ({
      country,
      sources: citations,
      present: present.has(country),
    })),
    flaggedNames: flaggedCountries(),
    sources,
  }
}

/** Build the filtered rows as CSV and hand them to the browser as a download. */
export async function downloadCsv(filters) {
  const store = await ensureStore()
  const sel = resolveSelection(store, filters)
  const csv = buildDownloadCsv(store, filters)

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `lead_trade_${sel.label}_${sel.yearStart}-${sel.yearEnd}.csv`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

// --- Geo cascade (mirrors src/filters.py) --------------------------------
const uniqSorted = (values) =>
  [...new Set(values)].sort((a, b) => String(a).localeCompare(String(b)))

export function availableSubregions(hierarchy, region) {
  let rows = hierarchy.filter((r) => r.subregion != null)
  if (region) rows = rows.filter((r) => r.region === region)
  return uniqSorted(rows.map((r) => r.subregion))
}

export function availableIntermediates(hierarchy, region, subregion) {
  let rows = hierarchy.filter((r) => r.intermediate_region != null)
  if (region) rows = rows.filter((r) => r.region === region)
  if (subregion) rows = rows.filter((r) => r.subregion === subregion)
  return uniqSorted(rows.map((r) => r.intermediate_region))
}

export function availableCountries(hierarchy, region, subregion, intermediate) {
  let rows = hierarchy.filter((r) => r.name != null)
  if (region) rows = rows.filter((r) => r.region === region)
  if (subregion) rows = rows.filter((r) => r.subregion === subregion)
  if (intermediate) rows = rows.filter((r) => r.intermediate_region === intermediate)
  return uniqSorted(rows.map((r) => r.name))
}

// name <-> iso helpers for the ?country= URL param.
export function isoForName(hierarchy, name) {
  const row = hierarchy.find((r) => r.name === name)
  return row?.iso_3 ? String(row.iso_3).toUpperCase() : null
}

export function nameForParam(hierarchy, raw) {
  if (!raw) return null
  const q = String(raw).trim().toUpperCase()
  const byIso = hierarchy.find((r) => r.iso_3 && String(r.iso_3).toUpperCase() === q)
  if (byIso) return byIso.name
  const byName = hierarchy.find((r) => r.name && r.name.toUpperCase() === q)
  return byName ? byName.name : null
}
