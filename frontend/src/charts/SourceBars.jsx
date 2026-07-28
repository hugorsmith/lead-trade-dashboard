import { useMeasure, useTooltip, Tooltip } from './ChartCard'
import { band, linear, ticks, compact, label, capped } from './primitives'

const M = { top: 6, right: 78, bottom: 24, left: 148 }

/**
 * Import sources for one year, with flagged countries highlighted.
 *
 * Colour here means *status*, not identity, so it never carries the meaning
 * alone: a flagged row also gets a marker glyph and the word "flagged" in its
 * label and tooltip. No categorical series colours appear in this chart, which
 * keeps the flag red from being mistaken for a product.
 */
export default function SourceBars({ sources, flagged, flagColor, rowHeight = 26, unit = 'tons' }) {
  const [ref, width] = useMeasure()
  const { tip, show, hide } = useTooltip()

  const names = sources.map((s) => s.name)
  const { max, values: tickValues } = ticks(Math.max(...sources.map((s) => s.value), 0), 4)

  const height = M.top + M.bottom + sources.length * rowHeight
  const plotW = Math.max(width - M.left - M.right, 0)
  const y = band(names, [M.top, M.top + sources.length * rowHeight], { maxBand: 18, padding: 0.34 })
  const x = linear(max, [M.left, M.left + plotW])

  return (
    <div className="plot-host" ref={ref}>
      {width > 0 && (
        <svg width={width} height={height} role="img"
             aria-label={`Import sources ranked by volume in ${unit}; countries flagged for unsafe recycling are marked`}>
          {tickValues.map((t) => (
            <g key={t}>
              <line className="grid" x1={x(t)} x2={x(t)} y1={M.top} y2={M.top + sources.length * rowHeight} />
              <text className="tick" x={x(t)} y={height - 8} textAnchor="middle">{compact(t)}</text>
            </g>
          ))}

          {sources.map((s) => {
            const isFlagged = flagged.has(s.name)
            const w = Math.max(x(s.value) - M.left, 0.75)
            return (
              <g key={s.name}>
                <text
                  className={isFlagged ? 'row-label flagged' : 'row-label'}
                  x={M.left - 12} y={y.center(s.name)} dy="0.32em" textAnchor="end"
                >
                  {isFlagged ? `⚑ ${s.name}` : s.name}
                </text>
                <path
                  d={capped(M.left, y(s.name), w, y.thickness, 4, 'right')}
                  fill={isFlagged ? flagColor : 'var(--neutral-mark)'}
                  opacity={tip && tip.content.title !== s.name ? 0.45 : 1}
                />
                <text className="row-value" x={x(s.value) + 10} y={y.center(s.name)} dy="0.32em">
                  {label(s.value)}
                </text>
              </g>
            )
          })}

          {sources.map((s) => (
            <rect
              key={`hit-${s.name}`}
              className="hit"
              x={M.left} y={y.center(s.name) - rowHeight / 2} width={plotW} height={rowHeight}
              onPointerMove={(e) => show(e, {
                title: s.name,
                rows: [{
                  label: flagged.has(s.name) ? 'flagged for unsafe ULAB recycling' : 'tons imported by the USA',
                  value: s.value,
                  color: flagged.has(s.name) ? flagColor : 'var(--neutral-mark)',
                }],
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
