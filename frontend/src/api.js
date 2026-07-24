// Data access + client-side geo cascade.
//
// There is no backend. The browser loads two static assets once
// (data/meta.json + data/trade.tsv, produced by scripts/export_data.py) and
// every KPI, aggregation and Plotly figure is computed here on demand.
//
// The functions below keep the request/response *shapes* the old FastAPI
// endpoints returned, so the components consuming them didn't have to change.
// They stay async because the first call has to await the initial data load.
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
  buildMapData,
} from './data/aggregations.js'
import {
  buildCategoryTradeFigure,
  buildHsBarFigure,
  buildTopPartnersFigure,
  buildSafetyFigure,
  buildMapFigure,
} from './data/figures.js'
import { FLAG_COLOR, UNSAFE_SOURCES, flaggedCountries } from './data/safety.js'

// --- One-time load --------------------------------------------------------
let _store = null
let _loading = null

/** Load (once) and return the in-browser data store. */
export function ensureStore() {
  if (!_loading) _loading = loadStore().then((s) => (_store = s))
  return _loading
}

/** Refined lead ("New Lead") HS codes — the fixed scope of the safety view. */
const newLeadCodes = (store) =>
  store.products.allCodes.filter((c) => store.products.toCategory[c] === 'New Lead')

// --- "Endpoints" ----------------------------------------------------------

export async function fetchMeta() {
  const store = await ensureStore()
  return store.meta
}

/** KPIs + the category subplot, both HS-code bar charts, and the map. */
export async function fetchDashboard(filters) {
  const store = await ensureStore()
  const theme = filters.theme ?? 'dark'
  const sel = resolveSelection(store, filters)

  const yearlyExports = aggregateByHsYear(store, sel.exportIdx)
  const yearlyImports = aggregateByHsYear(store, sel.importIdx)
  const categoryTrade = aggregateCategoryTrade(store, sel.exportIdx, sel.importIdx, store.products)
  const mapData = buildMapData(store, sel.exportIdx, sel.importIdx, sel.mapYear)

  return {
    label: sel.label,
    metrics_year: sel.metricsYear,
    map_year: sel.mapYear,
    year_start: sel.yearStart,
    year_end: sel.yearEnd,
    kpis: computeKpis(store, sel.exportIdx, sel.importIdx, sel.metricsYear),
    export_years: sel.exportYears,
    import_years: sel.importYears,
    figures: {
      category_trade: buildCategoryTradeFigure(categoryTrade, store.products, theme),
      exports_by_hs: buildHsBarFigure(yearlyExports, sel.selectedCodes, store.products, theme),
      imports_by_hs: buildHsBarFigure(yearlyImports, sel.selectedCodes, store.products, theme),
      map: buildMapFigure(
        mapData, store,
        `Net Trade Partners for ${sel.label} (${sel.mapYear})`,
        theme,
      ),
    },
  }
}

/** Top-20 destinations (exports) or sources (imports) for a chosen year. */
export async function fetchTop(filters) {
  const store = await ensureStore()
  const { direction, year, theme = 'dark' } = filters
  const sel = resolveSelection(store, filters)

  const isExports = direction === 'exports'
  const idx = isExports ? sel.exportIdx : sel.importIdx
  const partnerCol = isExports ? 'importer' : 'exporter'

  const top = topPartners(store, idx, partnerCol, year)

  return {
    direction,
    year,
    figure: buildTopPartnersFigure(top, partnerCol, store, sel.selectedCodes, store.products, theme),
    available_years: isExports ? sel.exportYears : sel.importYears,
  }
}

/** US refined-lead import sources, flagged by unsafe-ULAB-recycling status. */
export async function fetchSafety({ year, theme = 'dark' } = {}) {
  const store = await ensureStore()

  // Fixed scope: imports INTO the USA, refined lead ("New Lead") only.
  const sel = resolveSelection(store, { products: newLeadCodes(store), country: 'USA' })
  const availableYears = sel.importYears
  const selectedYear = year ?? availableYears[0] ?? sel.yearEnd

  const totals = totalByPartner(store, sel.importIdx, 'exporter', selectedYear, 25)
  const flagged = flaggedCountries()

  // Only surface flagged countries that actually appear as sources this year.
  const present = new Set(totals.map((t) => store.nameOf(t.partner)))

  return {
    year: selectedYear,
    available_years: availableYears,
    flag_color: FLAG_COLOR,
    flagged: Object.entries(UNSAFE_SOURCES).map(([country, sources]) => ({
      country,
      sources,
      present: present.has(country),
    })),
    figure: buildSafetyFigure(totals, store, flagged, FLAG_COLOR, theme),
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
