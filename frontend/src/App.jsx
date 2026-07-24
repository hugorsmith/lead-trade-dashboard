import { useEffect, useMemo, useState } from 'react'
import {
  fetchMeta, fetchDashboard, fetchTop, downloadCsv,
  isoForName, nameForParam,
} from './api'
import Filters from './components/Filters'
import KpiRow from './components/KpiRow'
import PlotlyFigure from './components/PlotlyFigure'
import Tabs from './components/Tabs'
import ProductDefinitions from './components/ProductDefinitions'
import SafetyView from './components/SafetyView'

// Refined lead ("New Lead") — the products this dashboard most wants to track;
// the default selection so people start on refined-lead trade.
const NEW_LEAD_CODES = ['780110', '780191', '780199']
const SAFETY_HASH = '#us-refined-lead-safety'

// Build the query object shared by every endpoint from the current filter state.
function buildParams(filters, theme) {
  const [year_start, year_end] = filters.years ?? [null, null]
  return {
    products: filters.products ?? undefined, // undefined => backend uses all
    year_start,
    year_end,
    region: filters.region,
    subregion: filters.subregion,
    intermediate: filters.intermediate,
    country: filters.country,
    theme,
  }
}

export default function App() {
  const [meta, setMeta] = useState(null)
  const [error, setError] = useState(null)
  const [theme, setTheme] = useState('dark')
  // Default landing view: Nigeria's refined-lead trade (top destination: USA).
  const [filters, setFilters] = useState({
    products: NEW_LEAD_CODES, years: null, region: null, subregion: null, intermediate: null, country: 'Nigeria',
  })

  const [dashboard, setDashboard] = useState(null)
  const [exportTop, setExportTop] = useState(null)
  const [importTop, setImportTop] = useState(null)
  const [exportYear, setExportYear] = useState(null)
  const [importYear, setImportYear] = useState(null)
  const [loading, setLoading] = useState(false)
  const [route, setRoute] = useState(window.location.hash)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
  }, [theme])

  useEffect(() => {
    const onHash = () => setRoute(window.location.hash)
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  useEffect(() => {
    fetchMeta()
      .then(setMeta)
      .catch((e) => setError(String(e)))
  }, [])

  // On first load, honour a ?country=NGA (ISO-3) URL parameter.
  useEffect(() => {
    if (!meta) return
    const raw = new URLSearchParams(window.location.search).get('country')
    const name = nameForParam(meta.hierarchy, raw)
    if (name && name !== filters.country) {
      setFilters((f) => ({ ...f, region: null, subregion: null, intermediate: null, country: name }))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [meta])

  // Keep the URL's ?country= in sync with the selected country (shareable links).
  useEffect(() => {
    if (!meta) return
    const iso = isoForName(meta.hierarchy, filters.country)
    const url = new URL(window.location.href)
    if (iso) url.searchParams.set('country', iso)
    else url.searchParams.delete('country')
    window.history.replaceState({}, '', url)
  }, [meta, filters.country])

  const params = useMemo(() => buildParams(filters, theme), [filters, theme])
  const paramsKey = JSON.stringify(params)
  const noProducts = Array.isArray(filters.products) && filters.products.length === 0
  const onSafety = route === SAFETY_HASH

  // Main dashboard fetch (debounced) whenever filters/theme change.
  useEffect(() => {
    if (!meta || noProducts || onSafety) return
    let cancelled = false
    setLoading(true)
    const t = setTimeout(() => {
      fetchDashboard(params)
        .then((d) => {
          if (cancelled) return
          setDashboard(d)
          setExportYear(d.export_years[0] ?? null)
          setImportYear(d.import_years[0] ?? null)
        })
        .catch((e) => !cancelled && setError(String(e)))
        .finally(() => !cancelled && setLoading(false))
    }, 250)
    return () => { cancelled = true; clearTimeout(t) }
  }, [paramsKey, meta, noProducts, onSafety])

  // Top-destinations chart (its own year selector).
  useEffect(() => {
    if (!meta || noProducts || onSafety || exportYear == null) return
    let cancelled = false
    fetchTop({ ...params, direction: 'exports', year: exportYear })
      .then((r) => !cancelled && setExportTop(r))
      .catch((e) => !cancelled && setError(String(e)))
    return () => { cancelled = true }
  }, [paramsKey, meta, noProducts, onSafety, exportYear])

  // Top-sources chart (its own year selector).
  useEffect(() => {
    if (!meta || noProducts || onSafety || importYear == null) return
    let cancelled = false
    fetchTop({ ...params, direction: 'imports', year: importYear })
      .then((r) => !cancelled && setImportTop(r))
      .catch((e) => !cancelled && setError(String(e)))
    return () => { cancelled = true }
  }, [paramsKey, meta, noProducts, onSafety, importYear])

  if (error) return <div className="fatal">Error: {error}</div>
  if (!meta) return <div className="loading-screen">Loading trade data…</div>

  const goSafety = () => { window.location.hash = SAFETY_HASH.slice(1) }
  const goDashboard = () => { window.location.hash = '' }

  if (onSafety) {
    return (
      <div className="layout">
        <TopBar meta={meta} theme={theme} setTheme={setTheme} onSafety={goSafety} />
        <SafetyView theme={theme} onBack={goDashboard} />
      </div>
    )
  }

  const label = dashboard?.label ?? ''
  const onDownload = () => downloadCsv({ ...params, theme: undefined })

  // Destinations/sources chart FIRST, over-time chart underneath.
  const exportsTab = (
    <div className="chart-stack">
      <ChartCard
        title={`Top Export Destinations for ${label}`}
        control={<YearSelect years={dashboard?.export_years ?? []} value={exportYear} onChange={setExportYear} />}
      >
        <PlotlyFigure figure={exportTop?.figure} height={520} />
      </ChartCard>
      <ChartCard title={`Export Volumes for ${label} by HS Code (over time)`}>
        <PlotlyFigure figure={dashboard?.figures.exports_by_hs} height={520} />
      </ChartCard>
    </div>
  )

  const importsTab = (
    <div className="chart-stack">
      <ChartCard
        title={`Top Import Sources for ${label}`}
        control={<YearSelect years={dashboard?.import_years ?? []} value={importYear} onChange={setImportYear} />}
      >
        <PlotlyFigure figure={importTop?.figure} height={520} />
      </ChartCard>
      <ChartCard title={`Import Volumes for ${label} by HS Code (over time)`}>
        <PlotlyFigure figure={dashboard?.figures.imports_by_hs} height={520} />
      </ChartCard>
    </div>
  )

  return (
    <div className="layout">
      <TopBar meta={meta} theme={theme} setTheme={setTheme} onSafety={goSafety} />

      <div className="body">
        <Filters meta={meta} filters={filters} setFilters={setFilters} onDownload={onDownload} />

        <main className="content">
          {noProducts ? (
            <div className="warn-banner">Select at least one product to see data.</div>
          ) : (
            <>
              <div className="content-header">
                <h2>{label}</h2>
                {loading && <span className="spinner">updating…</span>}
              </div>

              <KpiRow kpis={dashboard?.kpis} />

              <Tabs
                tabs={[
                  { label: 'Exports Analysis', content: exportsTab },
                  { label: 'Imports Analysis', content: importsTab },
                ]}
              />

              <ChartCard title={`Net Trade Partners${dashboard ? ` (${dashboard.map_year})` : ''}`}>
                <PlotlyFigure figure={dashboard?.figures.map} height={460} />
              </ChartCard>

              <ChartCard title={`Exports and Imports for ${label} by Category`}>
                <PlotlyFigure figure={dashboard?.figures.category_trade} height={420} />
              </ChartCard>
            </>
          )}

          <ProductDefinitions categories={meta.categories} />
        </main>
      </div>
    </div>
  )
}

function TopBar({ meta, theme, setTheme, onSafety }) {
  return (
    <header className="topbar">
      <div>
        <h1>Global Lead Trade Analysis Dashboard</h1>
        <p className="subtitle">Global lead trade data {meta.year_min}–{meta.year_max} · CEPII BACI dataset · Weight in tons</p>
      </div>
      <div className="topbar-actions">
        <a className="substack-badge" href="https://leadbatteries.substack.com/" target="_blank" rel="noreferrer">📚 Lead Battery Notes</a>
        <a className="link" href="https://github.com/hugorsmith/lead-trade-data" target="_blank" rel="noreferrer">🔗 Data</a>
        <a className="link" href="#product-definitions">⬇ Product Codes</a>
        <button className="safety-btn" onClick={onSafety}>
          ⚠ See US refined-lead imports by safety of source
        </button>
        <button className="theme-toggle" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
          {theme === 'dark' ? '☀ Light' : '☾ Dark'}
        </button>
      </div>
    </header>
  )
}

function ChartCard({ title, control, children }) {
  return (
    <section className="chart-card">
      <div className="chart-card-head">
        <h3>{title}</h3>
        {control}
      </div>
      {children}
    </section>
  )
}

function YearSelect({ years, value, onChange }) {
  return (
    <label className="year-select">
      <span>Year</span>
      <select value={value ?? ''} onChange={(e) => onChange(Number(e.target.value))}>
        {years.map((y) => (
          <option key={y} value={y}>{y}</option>
        ))}
      </select>
    </label>
  )
}
