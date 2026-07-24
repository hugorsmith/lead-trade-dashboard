import { full } from '../charts/primitives'

/**
 * The four headline figures.
 *
 * Deltas are deliberately not coloured green/red: a rise in traded tonnage is
 * neither good nor bad here, and status colours are reserved for the safety
 * view, where they actually mean something. Direction is carried by a glyph
 * and the sign instead.
 */
function Tile({ label, value, unit, delta, since }) {
  return (
    <div className="kpi">
      <p className="kpi-label">{label}</p>
      <p className="kpi-value">
        {value}
        {unit && <span className="kpi-unit">{unit}</span>}
      </p>
      {delta !== undefined && Number.isFinite(delta) && (
        <p className="kpi-delta">
          <span aria-hidden="true">{delta >= 0 ? '▲' : '▼'}</span>{' '}
          {delta >= 0 ? '+' : '−'}{Math.abs(delta).toFixed(1)}% vs {since}
        </p>
      )}
    </div>
  )
}

export default function KpiRow({ kpis, label }) {
  if (!kpis) return null
  const since = kpis.metrics_year - 1

  return (
    <section className="kpi-row" aria-label={`Key figures for ${label} in ${kpis.metrics_year}`}>
      <p className="kpi-caption">
        {label} · {kpis.metrics_year}
      </p>
      <div className="kpi-grid">
        <Tile label="Exported" value={full(kpis.total_exports)} unit="t" delta={kpis.export_change} since={since} />
        <Tile label="Imported" value={full(kpis.total_imports)} unit="t" delta={kpis.import_change} since={since} />
        <Tile label="Trade balance" value={full(kpis.trade_balance)} unit="t" />
        <Tile label="Trading partners" value={kpis.num_partners.toLocaleString()} />
      </div>
    </section>
  )
}
