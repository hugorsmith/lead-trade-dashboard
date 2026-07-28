// In-browser data store — the port of backend/store.py.
//
// Loads the two static assets produced by scripts/export_data.py exactly once
// (the browser equivalent of the server's module-level load), keeps the trade
// rows in columnar typed arrays, and reproduces the product/year/geography
// filtering the API used to do per request.
//
// Countries are stored as ISO-3 indices rather than names: the source data has
// a clean 1:1 ISO-3 <-> name mapping, so this is equivalent to the server's
// name-based joins while being smaller and faster to compare.

import { buildProductIndex } from './config.js'

const BASE = import.meta.env?.BASE_URL || '/'
const dataUrl = (file) => `${BASE}data/${file}`

/** Parse trade.tsv into columnar typed arrays. */
function parseTrade(text, isoIndex, productIndex) {
  // Trim a single trailing newline, then drop the header row.
  const start = text.indexOf('\n') + 1
  const end = text.charCodeAt(text.length - 1) === 10 ? text.length - 1 : text.length
  const lines = text.slice(start, end).split('\n')
  const n = lines.length

  const year = new Int16Array(n)
  const exporter = new Int16Array(n)
  const importer = new Int16Array(n)
  const product = new Int8Array(n)
  const value = new Float64Array(n)
  const quantity = new Float64Array(n)

  for (let i = 0; i < n; i++) {
    const f = lines[i].split('\t')
    year[i] = +f[0]
    exporter[i] = isoIndex.get(f[1])
    importer[i] = isoIndex.get(f[2])
    product[i] = productIndex.get(f[3])
    value[i] = +f[4]
    // An empty quantity means "not reported"; it sums as 0, matching pandas.
    quantity[i] = f[5] === '' ? 0 : +f[5]
  }

  return { n, year, exporter, importer, product, value, quantity }
}

/** Fetch + parse meta.json and trade.tsv. Resolves to the store singleton. */
export async function loadStore() {
  const [metaRes, tradeRes] = await Promise.all([
    fetch(dataUrl('meta.json')),
    fetch(dataUrl('trade.tsv')),
  ])
  if (!metaRes.ok) throw new Error(`meta.json unavailable (${metaRes.status})`)
  if (!tradeRes.ok) throw new Error(`trade.tsv unavailable (${tradeRes.status})`)

  const meta = await metaRes.json()
  const text = await tradeRes.text()

  const products = buildProductIndex(meta.categories)
  const productCodes = products.allCodes
  const productIndex = new Map(productCodes.map((c, i) => [c, i]))

  // ISO-3 universe comes from the geo hierarchy, which export_data.py already
  // restricted to countries present in the trade data.
  const iso = meta.hierarchy.map((r) => r.iso_3)
  const isoIndex = new Map(iso.map((c, i) => [c, i]))
  const names = new Map(meta.hierarchy.map((r) => [r.iso_3, r.name]))
  const nameToIso = new Map(meta.hierarchy.map((r) => [r.name, r.iso_3]))

  const columns = parseTrade(text, isoIndex, productIndex)

  return {
    ...columns,
    meta,
    products,
    productCodes,
    productIndex,
    iso,
    isoIndex,
    names,
    nameToIso,
    /** ISO index -> display name, for chart labels. */
    nameOf: (isoIdx) => names.get(iso[isoIdx]) ?? iso[isoIdx],
  }
}

/**
 * Resolve the geographic filters to the set of selected ISO indices.
 * `country` wins; otherwise the region > subregion > intermediate cascade.
 * Returns null to mean "all countries" (no geographic restriction).
 */
function selectedIsoSet(store, { region, subregion, intermediate, country }) {
  if (country) {
    const code = store.nameToIso.get(country)
    const idx = store.isoIndex.get(code)
    return idx === undefined ? new Set() : new Set([idx])
  }
  if (!region && !subregion && !intermediate) return null

  const set = new Set()
  for (const r of store.meta.hierarchy) {
    if (r.name == null) continue
    if (region && r.region !== region) continue
    if (subregion && r.subregion !== subregion) continue
    if (intermediate && r.intermediate_region !== intermediate) continue
    const idx = store.isoIndex.get(r.iso_3)
    if (idx !== undefined) set.add(idx)
  }
  return set
}

/**
 * Reproduce the API's per-request filtering (backend/store.py: resolve_selection).
 *
 * @returns {{
 *   exportIdx: number[], importIdx: number[],
 *   selectedCodes: string[], label: string,
 *   metricsYear: number, yearStart: number, yearEnd: number,
 *   exportYears: number[], importYears: number[], mapYear: number,
 * }}
 */
export function resolveSelection(store, filters = {}) {
  // Filter keys are snake_case: the shape App.jsx builds and the old API took.
  const {
    products, year_start: yearStart, year_end: yearEnd,
    region, subregion, intermediate, country,
  } = filters

  const selectedCodes = products?.length ? products : store.products.allCodes
  const start = yearStart ?? store.meta.year_min
  const end = yearEnd ?? store.meta.year_max

  // Product mask as a boolean lookup over product indices (only 8 of them).
  const productMask = new Uint8Array(store.productCodes.length)
  for (const code of selectedCodes) {
    const i = store.productIndex.get(code)
    if (i !== undefined) productMask[i] = 1
  }

  const isoSet = selectedIsoSet(store, { region, subregion, intermediate, country })

  const exportIdx = []
  const importIdx = []
  // metricsYear mirrors the server's df_filtered.year.max(): the latest year in
  // the product/year mask across *all* countries, not just the selection.
  let metricsYear = -Infinity
  const exportYears = new Set()
  const importYears = new Set()

  const { n, year, exporter, importer, product } = store
  for (let i = 0; i < n; i++) {
    const y = year[i]
    if (y < start || y > end) continue
    if (!productMask[product[i]]) continue

    if (y > metricsYear) metricsYear = y

    if (isoSet === null || isoSet.has(exporter[i])) {
      exportIdx.push(i)
      exportYears.add(y)
    }
    if (isoSet === null || isoSet.has(importer[i])) {
      importIdx.push(i)
      importYears.add(y)
    }
  }

  if (metricsYear === -Infinity) metricsYear = end

  const label = country ?? intermediate ?? subregion ?? region ?? 'All Countries'
  const desc = (s) => [...s].sort((a, b) => b - a)
  const exportYearList = desc(exportYears)

  return {
    exportIdx,
    importIdx,
    selectedCodes,
    label,
    metricsYear,
    yearStart: start,
    yearEnd: end,
    exportYears: exportYearList,
    importYears: desc(importYears),
    // The map uses the latest year present in the selection's exports.
    mapYear: exportYearList.length ? exportYearList[0] : end,
  }
}

/**
 * Build the filtered-rows CSV the old /api/download endpoint streamed, but
 * assembled in the browser. Returns a CSV string.
 */
export function buildDownloadCsv(store, filters = {}) {
  const sel = resolveSelection(store, filters)
  // Union of both sides, in original row order (a row can be in only one of the
  // two when a specific country is selected, but not when a region is).
  const rowSet = new Set(sel.exportIdx)
  for (const i of sel.importIdx) rowSet.add(i)
  const rows = [...rowSet].sort((a, b) => a - b)

  const header = [
    'year', 'exporter_name', 'exporter_iso3', 'importer_name', 'importer_iso3',
    'product', 'product_label', 'value', 'quantity',
  ]
  const esc = (v) => {
    const s = String(v ?? '')
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
  }

  const out = [header.join(',')]
  for (const i of rows) {
    const expIso = store.iso[store.exporter[i]]
    const impIso = store.iso[store.importer[i]]
    const code = store.productCodes[store.product[i]]
    out.push([
      store.year[i],
      esc(store.names.get(expIso)), expIso,
      esc(store.names.get(impIso)), impIso,
      code, esc(store.products.labels[code]),
      store.value[i],
      store.quantity[i],
    ].join(','))
  }
  return out.join('\n')
}
