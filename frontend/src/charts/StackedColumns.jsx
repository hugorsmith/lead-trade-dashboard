import { useMeasure, useTooltip, Tooltip } from './ChartCard'
import { band, linear, ticks, compact, capped, stack, GAP } from './primitives'

const M = { top: 10, right: 8, bottom: 26, left: 58 }

/**
 * Volume over time, stacked by product.
 *
 * The hit target is the whole column band, not the painted segments — a 3-tonne
 * slice is a two-pixel sliver nobody can point at, and the tooltip lists every
 * series at that year anyway.
 */
export default function StackedColumns({ categories, series, height = 300, unit = 'tons' }) {
  const [ref, width] = useMeasure()
  const { tip, show, hide } = useTooltip()

  const stacks = categories.map((c, i) =>
    stack(series.map((s) => ({ key: s.key, label: s.label, color: s.color, value: s.values[i] ?? 0 })))
  )
  const { max, values: tickValues } = ticks(Math.max(...stacks.map((s) => s.total), 0))

  const plotW = Math.max(width - M.left - M.right, 0)
  const plotH = height - M.top - M.bottom
  const x = band(categories, [M.left, M.left + plotW], { maxBand: 34 })
  const y = linear(max, [M.top + plotH, M.top])

  return (
    <div className="plot-host" ref={ref}>
      {width > 0 && (
        <svg width={width} height={height} role="img"
             aria-label={`Stacked columns of volume in ${unit} by product, ${categories[0]} to ${categories[categories.length - 1]}`}>
          {tickValues.map((t) => (
            <g key={t}>
              <line className="grid" x1={M.left} x2={M.left + plotW} y1={y(t)} y2={y(t)} />
              <text className="tick" x={M.left - 10} y={y(t)} dy="0.32em" textAnchor="end">
                {compact(t)}
              </text>
            </g>
          ))}

          {categories.map((c, i) => (
            <g key={c}>
              {stacks[i].segments.map((seg) => {
                const top = y(seg.end)
                const h = Math.max(y(seg.start) - top - GAP, 0.75)
                return (
                  <path
                    key={seg.key}
                    d={capped(x(c), top, x.thickness, h, 4, 'up')}
                    fill={seg.color}
                    opacity={tip && tip.content.title !== String(c) ? 0.45 : 1}
                  />
                )
              })}
            </g>
          ))}

          {categories.map((c, i) => (
            <rect
              key={`hit-${c}`}
              className="hit"
              x={x.center(c) - x.step / 2} y={M.top} width={x.step} height={plotH}
              onPointerMove={(e) => show(e, {
                title: String(c),
                rows: stacks[i].segments.slice().reverse()
                  .map((s) => ({ label: s.label, value: s.value, color: s.color })),
              })}
              onPointerLeave={hide}
            />
          ))}

          {categories.map((c) => (
            <text key={`x-${c}`} className="tick" x={x.center(c)} y={height - 8} textAnchor="middle">
              {c}
            </text>
          ))}
        </svg>
      )}
      <Tooltip tip={tip} />
    </div>
  )
}
