import { useEffect, useState } from 'react'
import { fetchSafety } from '../api'
import ChartCard from '../charts/ChartCard'
import SourceBars from '../charts/SourceBars'

// Standalone "safety of source" page: US refined-lead import sources, with
// countries flagged for unsafe used lead-acid battery (ULAB) recycling marked.
export default function SafetyView({ onBack }) {
  const [data, setData] = useState(null)
  const [year, setYear] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    fetchSafety({ year })
      .then((d) => {
        if (cancelled) return
        setData(d)
        if (year == null) setYear(d.year)
      })
      .catch((e) => !cancelled && setError(String(e)))
    return () => { cancelled = true }
  }, [year])

  if (error) return <div className="fatal">Something went wrong: {error}</div>

  const flagColor = data?.flagColor ?? '#d03b3b'

  return (
    <main className="content safety">
      <button className="btn back" onClick={onBack}>← Back to the dashboard</button>

      <div className="safety-intro">
        <p className="eyebrow">Refined lead · imports into the USA</p>
        <h1>Where US refined lead comes from</h1>
        <p className="lede">
          Countries marked <span className="flag-token">⚑ flagged</span> have documented hazards from
          informal used lead-acid battery recycling. The mark, not the colour, carries the meaning.
        </p>
      </div>

      <ChartCard
        title="Import sources, ranked by volume"
        note={year ? `United States refined-lead imports in ${year}.` : null}
        control={data && (
          <label className="field compact">
            <span>Year</span>
            <select value={year ?? ''} onChange={(e) => setYear(Number(e.target.value))}>
              {data.available_years.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </label>
        )}
        table={data && {
          columns: ['Source', 'Tons', 'Status'],
          rows: data.sources.map((s) => [
            s.name,
            s.value,
            data.flaggedNames.has(s.name) ? 'Flagged — unsafe ULAB recycling' : 'Not flagged',
          ]),
        }}
      >
        {data && (
          <SourceBars
            sources={data.sources}
            flagged={data.flaggedNames}
            flagColor={flagColor}
          />
        )}
      </ChartCard>

      <section className="flagged-panel">
        <h2>Why these countries are flagged</h2>
        <div className="flagged-grid">
          {(data?.flagged ?? []).map((f) => (
            <article key={f.country} className="flagged-card">
              <h3>
                <span aria-hidden="true">⚑</span> {f.country}
                {!f.present && <span className="muted"> · no imports this year</span>}
              </h3>
              <ul>
                {f.sources.map((s) => (
                  <li key={s.url}>
                    <a href={s.url} target="_blank" rel="noreferrer">{s.title}</a>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
        <p className="hint">
          These citations are a starting point and under review.
        </p>
      </section>
    </main>
  )
}
