// Four headline KPI cards with YoY deltas. Formatting mirrors app.py:
//   value  -> "{:,.0f} mt"      delta -> "{:+.1f}% vs prev year"
const fmtVol = (n) => `${Math.round(n).toLocaleString('en-US')} mt`
const fmtDelta = (n) => `${n >= 0 ? '+' : ''}${n.toFixed(1)}% vs prev year`

function Card({ label, value, delta }) {
  const dir = delta === undefined ? '' : delta >= 0 ? 'up' : 'down'
  return (
    <div className="kpi-card">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {delta !== undefined && <div className={`kpi-delta ${dir}`}>{fmtDelta(delta)}</div>}
    </div>
  )
}

export default function KpiRow({ kpis }) {
  if (!kpis) return null
  return (
    <div className="kpi-row">
      <Card label="Total Export Volume" value={fmtVol(kpis.total_exports)} delta={kpis.export_change} />
      <Card label="Total Import Volume" value={fmtVol(kpis.total_imports)} delta={kpis.import_change} />
      <Card label="Trade Balance" value={fmtVol(kpis.trade_balance)} />
      <Card label="Trading Partners" value={kpis.num_partners.toLocaleString('en-US')} />
    </div>
  )
}
