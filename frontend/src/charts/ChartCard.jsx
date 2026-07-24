import { useCallback, useEffect, useRef, useState } from 'react'
import { full } from './primitives'

/**
 * The frame every chart sits in: title, optional control, legend, and a
 * chart/table switch.
 *
 * The table is not a nicety — three palette slots fall below 3:1 contrast on
 * white, so every value has to be reachable without relying on hue, and a
 * tooltip alone would gate it behind a hover.
 */
export default function ChartCard({ title, note, control, legend, table, children }) {
  const [view, setView] = useState('chart')

  return (
    <section className="card">
      <header className="card-head">
        <div className="card-titles">
          <h3>{title}</h3>
          {note && <p className="card-note">{note}</p>}
        </div>
        <div className="card-tools">
          {control}
          {table && (
            <div className="seg" role="group" aria-label="View as">
              <button
                type="button" aria-pressed={view === 'chart'}
                onClick={() => setView('chart')}
              >Chart</button>
              <button
                type="button" aria-pressed={view === 'table'}
                onClick={() => setView('table')}
              >Table</button>
            </div>
          )}
        </div>
      </header>

      {legend && view === 'chart' && <Legend items={legend} />}

      {/* Fall back to the chart if the table data isn't there yet — a reload can
          empty it while the switch is still set to "Table". */}
      {view === 'table' && table ? <DataTable {...table} /> : children}
    </section>
  )
}

/**
 * Identity channel for two or more series. A single-series chart gets none —
 * its title already says what is plotted, so a lone swatch just restates it.
 */
export function Legend({ items }) {
  if (!items || items.length < 2) return null
  return (
    <ul className="legend">
      {items.map((it) => (
        <li key={it.label}>
          <span className="legend-key" style={{ background: it.color }} aria-hidden="true" />
          <span>{it.label}</span>
        </li>
      ))}
    </ul>
  )
}

/** The WCAG-clean twin of the chart. */
export function DataTable({ columns, rows, unit = 'tons' }) {
  return (
    <div className="table-wrap">
      <table className="data-table">
        <caption className="sr-only">Chart data, in {unit}</caption>
        <thead>
          <tr>
            {columns.map((c, i) => (
              <th key={c} scope="col" className={i ? 'num' : undefined}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={String(row[0])}>
              {row.map((cell, i) => (
                i === 0
                  ? <th key={i} scope="row">{cell}</th>
                  : <td key={i} className="num">{typeof cell === 'number' ? full(cell) : cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/** Width observer so charts can lay themselves out against real pixels. */
export function useMeasure() {
  const ref = useRef(null)
  const [width, setWidth] = useState(0)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const ro = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width))
    ro.observe(el)
    setWidth(el.getBoundingClientRect().width)
    return () => ro.disconnect()
  }, [])

  return [ref, width]
}

/**
 * Hover/focus readout. Values lead and labels follow — the reader already knows
 * which mark they are pointing at and wants the number.
 */
export function useTooltip() {
  const [tip, setTip] = useState(null)
  const hide = useCallback(() => setTip(null), [])
  const show = useCallback((event, content) => {
    const host = event.currentTarget.closest('.plot-host')
    if (!host) return
    const box = host.getBoundingClientRect()
    setTip({
      x: event.clientX - box.left,
      y: event.clientY - box.top,
      content,
    })
  }, [])
  return { tip, show, hide }
}

export function Tooltip({ tip }) {
  if (!tip) return null
  const { x, y, content } = tip
  return (
    <div
      className="tooltip"
      role="status"
      style={{ transform: `translate(${x}px, ${y}px)` }}
    >
      <div className="tooltip-head">{content.title}</div>
      {content.rows.map((r) => (
        <div key={r.label} className="tooltip-row">
          <span className="tooltip-key" style={{ background: r.color }} aria-hidden="true" />
          <span className="tooltip-value">{full(r.value)}</span>
          <span className="tooltip-label">{r.label}</span>
        </div>
      ))}
    </div>
  )
}
