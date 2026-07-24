import { useEffect, useState } from 'react'
import { fetchSafety } from '../api'
import PlotlyFigure from './PlotlyFigure'

// Standalone "safety of source" page: US refined-lead import sources with
// countries flagged for unsafe ULAB recycling highlighted in red.
export default function SafetyView({ theme, onBack }) {
  const [data, setData] = useState(null)
  const [year, setYear] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    fetchSafety({ year, theme })
      .then((d) => {
        if (cancelled) return
        setData(d)
        if (year == null) setYear(d.year)
      })
      .catch((e) => !cancelled && setError(String(e)))
    return () => { cancelled = true }
  }, [year, theme])

  if (error) return <div className="fatal">Error: {error}</div>

  const flagColor = data?.flag_color ?? '#ef4444'

  return (
    <main className="content safety-view">
      <button className="back-link" onClick={onBack}>← Back to dashboard</button>

      <h1>US Refined Lead Imports by Safety of Source</h1>
      <p className="subtitle">
        Sources of refined lead imported into the United States. Countries in{' '}
        <span style={{ color: flagColor, fontWeight: 600 }}>red</span> have documented hazards
        from informal used lead-acid battery (ULAB) recycling.
      </p>

      <section className="chart-card">
        <div className="chart-card-head">
          <h3>Top Import Sources for USA (Refined Lead)</h3>
          {data && (
            <label className="year-select">
              <span>Year</span>
              <select value={year ?? ''} onChange={(e) => setYear(Number(e.target.value))}>
                {data.available_years.map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </label>
          )}
        </div>
        <PlotlyFigure figure={data?.figure} height={560} />
      </section>

      <section className="flagged-panel">
        <h2>Flagged for unsafe ULAB recycling</h2>
        <div className="flagged-grid">
          {(data?.flagged ?? []).map((f) => (
            <div key={f.country} className="flagged-card" style={{ borderColor: flagColor }}>
              <h3 style={{ color: flagColor }}>
                {f.country}
                {!f.present && <span className="flagged-absent"> (no imports this year)</span>}
              </h3>
              <ul>
                {f.sources.map((s) => (
                  <li key={s.url}>
                    <a href={s.url} target="_blank" rel="noreferrer">{s.title}</a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <p className="flagged-note">
          Citations are a starting point and under review — the project owner should confirm and
          expand the sources for each country.
        </p>
      </section>
    </main>
  )
}
