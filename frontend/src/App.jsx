import { useEffect, useMemo, useState } from 'react'
import { fetchMeta, fetchDashboard, fetchTop, downloadCsv, isoForName, nameForParam } from './api'
import Filters from './components/Filters'
import GeoRow from './components/GeoRow'
import KpiRow from './components/KpiRow'
import Tabs from './components/Tabs'
import ProductDefinitions from './components/ProductDefinitions'
import SafetyView from './components/SafetyView'
import ChartCard from './charts/ChartCard'
import StackedColumns from './charts/StackedColumns'
import PartnerBars from './charts/PartnerBars'
import CategoryMirror from './charts/CategoryMirror'

// Refined lead ("New Lead") — the products this dashboard most wants to track;
// the default selection so people start on refined-lead trade.
const NEW_LEAD_CODES = ['780110', '780191', '780199']
const SAFETY_HASH = '#us-refined-lead-safety'

// Build the query object shared by every endpoint from the current filter state.
function buildParams(filters) {
  const [year_start, year_end] = filters.years ?? [null, null]
  return {
    products: filters.products ?? undefined,
    year_start,
    year_end,
    region: filters.region,
    subregion: filters.subregion,
    intermediate: filters.intermediate,
    country: filters.country,
  }
}

const legendOf = (series) => series.map((s) => ({ label: s.label, color: s.color }))

export default function App() {
  const [meta, setMeta] = useState(null)
  const [error, setError] = useState(null)
  // Default landing view: global refined-lead trade. A ?country= ISO-3 query
  // parameter can still select a country on first load.
  const [filters, setFilters] = useState({
    products: NEW_LEAD_CODES, years: null, region: null, subregion: null, intermediate: null, country: null,
  })

  const [dashboard, setDashboard] = useState(null)
  const [exportTop, setExportTop] = useState(null)
  const [importTop, setImportTop] = useState(null)
  const [exportYear, setExportYear] = useState(null)
  const [importYear, setImportYear] = useState(null)
  const [loading, setLoading] = useState(false)
  const [route, setRoute] = useState(window.location.hash)

  useEffect(() => {
    const onHash = () => setRoute(window.location.hash)
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  useEffect(() => {
    fetchMeta().then(setMeta).catch((e) => setError(String(e)))
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

  const params = useMemo(() => buildParams(filters), [filters])
  const paramsKey = JSON.stringify(params)
  const noProducts = Array.isArray(filters.products) && filters.products.length === 0
  const onSafety = route === SAFETY_HASH

  useEffect(() => {
    if (!meta || noProducts || onSafety) return
    let cancelled = false
    setLoading(true)
    const t = setTimeout(() => {
      fetchDashboard(params)
        .then((d) => {
          if (cancelled) return
          setDashboard(d)
          setExportYear((y) => (d.export_years.includes(y) ? y : d.export_years[0] ?? null))
          setImportYear((y) => (d.import_years.includes(y) ? y : d.import_years[0] ?? null))
        })
        .catch((e) => !cancelled && setError(String(e)))
        .finally(() => !cancelled && setLoading(false))
    }, 200)
    return () => { cancelled = true; clearTimeout(t) }
  }, [paramsKey, meta, noProducts, onSafety])

  useEffect(() => {
    if (!meta || noProducts || onSafety || exportYear == null) return
    let cancelled = false
    fetchTop({ ...params, direction: 'exports', year: exportYear })
      .then((r) => !cancelled && setExportTop(r))
      .catch((e) => !cancelled && setError(String(e)))
    return () => { cancelled = true }
  }, [paramsKey, meta, noProducts, onSafety, exportYear])

  useEffect(() => {
    if (!meta || noProducts || onSafety || importYear == null) return
    let cancelled = false
    fetchTop({ ...params, direction: 'imports', year: importYear })
      .then((r) => !cancelled && setImportTop(r))
      .catch((e) => !cancelled && setError(String(e)))
    return () => { cancelled = true }
  }, [paramsKey, meta, noProducts, onSafety, importYear])

  if (error) return <div className="fatal">Something went wrong: {error}</div>
  if (!meta) return <div className="loading-screen"><span>Loading trade data</span></div>

  const goSafety = () => { window.location.hash = SAFETY_HASH.slice(1) }
  const goDashboard = () => { window.location.hash = '' }

  if (onSafety) {
    return (
      <div className="layout">
        <TopBar meta={meta} onSafety={goSafety} />
        <SafetyView onBack={goDashboard} />
      </div>
    )
  }

  const label = dashboard?.label ?? filters.country ?? 'All Countries'
  const years = dashboard?.years ?? []

  return (
    <div className="layout">
      <TopBar meta={meta} onSafety={goSafety} />

      <div className="body">
        <Filters
          meta={meta}
          filters={filters}
          setFilters={setFilters}
          onDownload={() => downloadCsv(params)}
        />

        <main className="content">
          <header className="dashboard-heading">
            <div>
              <p className="eyebrow">Trade explorer</p>
              <h2>{label || filters.country || 'Global trade'}</h2>
            </div>
            <p className="dashboard-selection">
              {filters.products.length} products · {(filters.years ?? [meta.year_min, meta.year_max]).join('–')}
            </p>
          </header>

          <section className="geo-panel" aria-label="Geographic filters">
            <p className="geo-panel-label">Geography</p>
            <GeoRow meta={meta} filters={filters} setFilters={setFilters} />
          </section>

          {noProducts ? (
            <p className="notice">Select at least one product to see data.</p>
          ) : (
            <div className={loading ? 'panels is-loading' : 'panels'}>
              <KpiRow kpis={dashboard?.kpis} label={label} />

              <ChartCard
                title={`Exports and imports for ${label} by category`}
                note="Exports above the line, imports below, on one shared scale."
                legend={dashboard ? legendOf(dashboard.categorySeries) : null}
                table={dashboard && {
                  columns: ['Year', ...dashboard.categorySeries.flatMap((c) => [`${c.label} — exported`, `${c.label} — imported`])],
                  rows: years.map((y, i) => [
                    String(y),
                    ...dashboard.categorySeries.flatMap((c) => [c.exports[i], c.imports[i]]),
                  ]),
                }}
              >
                {dashboard && (
                  <CategoryMirror years={years} categories={dashboard.categorySeries} />
                )}
              </ChartCard>

              <Tabs
                tabs={[
                  {
                    label: 'Exports',
                    content: (
                      <>
                        <VolumeCard
                          title={`Export volumes for ${label} by HS code`}
                          series={dashboard?.exportSeries}
                          years={years}
                        />
                        <PartnerCard
                          title={`Top export destinations for ${label}`}
                          axisLabel="Destination"
                          top={exportTop}
                          years={dashboard?.export_years}
                          year={exportYear}
                          onYear={setExportYear}
                        />
                      </>
                    ),
                  },
                  {
                    label: 'Imports',
                    content: (
                      <>
                        <VolumeCard
                          title={`Import volumes for ${label} by HS code`}
                          series={dashboard?.importSeries}
                          years={years}
                        />
                        <PartnerCard
                          title={`Top import sources for ${label}`}
                          axisLabel="Source"
                          top={importTop}
                          years={dashboard?.import_years}
                          year={importYear}
                          onYear={setImportYear}
                        />
                      </>
                    ),
                  },
                ]}
              />
            </div>
          )}

          <ProductDefinitions categories={meta.categories} />
        </main>
      </div>
    </div>
  )
}

function VolumeCard({ title, series, years }) {
  if (!series) return null
  return (
    <ChartCard
      title={title}
      legend={legendOf(series)}
      table={{
        columns: ['Year', ...series.map((s) => s.label)],
        rows: years.map((y, i) => [String(y), ...series.map((s) => s.values[i])]),
      }}
    >
      {series.length ? (
        <StackedColumns categories={years} series={series} />
      ) : (
        <p className="notice">No trade recorded for this selection.</p>
      )}
    </ChartCard>
  )
}

function PartnerCard({ title, axisLabel, top, years, year, onYear }) {
  const control = years?.length ? (
    <label className="field compact">
      <span>Year</span>
      <select value={year ?? ''} onChange={(e) => onYear(Number(e.target.value))}>
        {years.map((y) => <option key={y} value={y}>{y}</option>)}
      </select>
    </label>
  ) : null

  return (
    <ChartCard
      title={title}
      note={year ? `Ranked by volume in ${year}.` : null}
      control={control}
      legend={top ? legendOf(top.series) : null}
      table={top && {
        columns: [axisLabel, ...top.series.map((s) => s.label), 'Total'],
        rows: top.partners.map((p, i) => [
          p,
          ...top.series.map((s) => s.values[i]),
          top.series.reduce((sum, s) => sum + (s.values[i] ?? 0), 0),
        ]),
      }}
    >
      {top?.partners.length ? (
        <PartnerBars partners={top.partners} series={top.series} />
      ) : (
        <p className="notice">No partners recorded for this selection.</p>
      )}
    </ChartCard>
  )
}

function TopBar({ meta, onSafety }) {
  return (
    <header className="topbar">
      <div className="brand">
        <p className="eyebrow">CEPII BACI · {meta.year_min}–{meta.year_max} · weight in tons</p>
        <h1>Global Lead Trade</h1>
      </div>
      <nav className="topbar-actions">
        <button className="btn btn-flag" onClick={onSafety}>
          US imports by safety of source
        </button>
        <a className="btn" href="#product-definitions">HS codes</a>
        <a className="btn" href="https://github.com/hugorsmith/lead-trade-data" target="_blank" rel="noreferrer">Data</a>
        <a className="btn" href="https://leadbatteries.substack.com/" target="_blank" rel="noreferrer">Lead Battery Notes</a>
      </nav>
    </header>
  )
}
