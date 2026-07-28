import { useMeasure, useTooltip, Tooltip } from './ChartCard'
import { band, linear, ticks, compact, label, capped, stack, GAP } from './primitives'

const M = { top: 6, right: 74, bottom: 24, left: 132 }

/**
 * Top trading partners, stacked by product.
 *
 * Horizontal, unlike the original: twenty country names on a vertical axis had
 * to be rotated 30 degrees to fit, which is hard to read and still collided.
 * Lying the bars down gives every name a full horizontal line and leaves room
 * for the total at each bar's tip — which is also the relief the low-contrast
 * palette slots require.
 */
export default function PartnerBars({ partners, series, rowHeight = 26, unit = 'tons' }) {
  const [ref, width] = useMeasure()
  const { tip, show, hide } = useTooltip()

  const stacks = partners.map((p, i) =>
    stack(series.map((s) => ({ key: s.key, label: s.label, color: s.color, value: s.values[i] ?? 0 })))
  )
  const { max, values: tickValues } = ticks(Math.max(...stacks.map((s) => s.total), 0), 4)

  const height = M.top + M.bottom + partners.length * rowHeight
  const plotW = Math.max(width - M.left - M.right, 0)
  const y = band(partners, [M.top, M.top + partners.length * rowHeight], { maxBand: 18, padding: 0.34 })
  const x = linear(max, [M.left, M.left + plotW])

  return (
    <div className="plot-host" ref={ref}>
      {width > 0 && (
        <svg width={width} height={height} role="img"
             aria-label={`Horizontal stacked bars of the top ${partners.length} partners by volume in ${unit}`}>
          {tickValues.map((t) => (
            <g key={t}>
              <line className="grid" x1={x(t)} x2={x(t)} y1={M.top} y2={M.top + partners.length * rowHeight} />
              <text className="tick" x={x(t)} y={height - 8} textAnchor="middle">{compact(t)}</text>
            </g>
          ))}

          {partners.map((p, i) => (
            <g key={p}>
              <text className="row-label" x={M.left - 12} y={y.center(p)} dy="0.32em" textAnchor="end">
                {p}
              </text>
              {stacks[i].segments.map((seg) => {
                const left = x(seg.start)
                const w = Math.max(x(seg.end) - left - GAP, 0.75)
                return (
                  <path
                    key={seg.key}
                    d={capped(left, y(p), w, y.thickness, 4, 'right')}
                    fill={seg.color}
                    opacity={tip && tip.content.title !== p ? 0.45 : 1}
                  />
                )
              })}
              <text className="row-value" x={x(stacks[i].total) + 10} y={y.center(p)} dy="0.32em">
                {label(stacks[i].total)}
              </text>
            </g>
          ))}

          {partners.map((p, i) => (
            <rect
              key={`hit-${p}`}
              className="hit"
              x={M.left} y={y.center(p) - rowHeight / 2} width={plotW} height={rowHeight}
              onPointerMove={(e) => show(e, {
                title: p,
                rows: stacks[i].segments.slice().reverse()
                  .map((s) => ({ label: s.label, value: s.value, color: s.color })),
              })}
              onPointerLeave={hide}
            />
          ))}
        </svg>
      )}
      <Tooltip tip={tip} />
    </div>
  )
}
