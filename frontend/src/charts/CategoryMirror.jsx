import { useMeasure, useTooltip, Tooltip } from './ChartCard'
import { band, ticks, compact, capped, stack, GAP } from './primitives'

const M = { top: 12, right: 8, bottom: 26, left: 70 }
/** Below this an arm has no room for its own ticks and label. */
const ARM_LABEL_MIN = 34

/**
 * Exports above the line, imports below, stacked by category.
 *
 * One shared pixels-per-tonne across both arms, but each arm is only as tall as
 * its own maximum. The original drew imports on a separate axis scaled to the
 * import maximum, which made a tiny import year look as tall as a huge export
 * year — the halves were not comparable even though sharing an x-axis invites
 * exactly that comparison. Splitting the height evenly instead would be honest
 * but wastes half the card whenever one side dwarfs the other, which is the
 * common case here.
 */
export default function CategoryMirror({ years, categories, height = 320, unit = 'tons' }) {
  const [ref, width] = useMeasure()
  const { tip, show, hide } = useTooltip()

  const arms = years.map((_, i) => ({
    exports: stack(categories.map((c) => ({ key: c.key, label: c.label, color: c.color, value: c.exports[i] ?? 0 }))),
    imports: stack(categories.map((c) => ({ key: c.key, label: c.label, color: c.color, value: c.imports[i] ?? 0 }))),
  }))

  const peakExports = Math.max(...arms.map((a) => a.exports.total), 0)
  const peakImports = Math.max(...arms.map((a) => a.imports.total), 0)
  const up = ticks(peakExports, 3)
  const down = ticks(peakImports, 2)

  const plotW = Math.max(width - M.left - M.right, 0)
  const plotH = height - M.top - M.bottom
  const span = up.max + down.max || 1
  const perUnit = plotH / span               // shared scale, both directions
  const upArm = up.max * perUnit
  const downArm = down.max * perUnit
  const center = M.top + upArm
  const len = (v) => v * perUnit

  const x = band(years, [M.left, M.left + plotW], { maxBand: 34 })
  const showUpAxis = upArm >= ARM_LABEL_MIN
  const showDownAxis = downArm >= ARM_LABEL_MIN

  return (
    <div className="plot-host" ref={ref}>
      {width > 0 && (
        <svg width={width} height={height} role="img"
             aria-label={`Exports above and imports below a shared baseline, stacked by category, in ${unit}`}>
          {showUpAxis && up.values.filter((t) => t > 0).map((t) => (
            <g key={`u${t}`}>
              <line className="grid" x1={M.left} x2={M.left + plotW} y1={center - len(t)} y2={center - len(t)} />
              <text className="tick" x={M.left - 10} y={center - len(t)} dy="0.32em" textAnchor="end">{compact(t)}</text>
            </g>
          ))}
          {showDownAxis && down.values.filter((t) => t > 0).map((t) => (
            <g key={`d${t}`}>
              <line className="grid" x1={M.left} x2={M.left + plotW} y1={center + len(t)} y2={center + len(t)} />
              <text className="tick" x={M.left - 10} y={center + len(t)} dy="0.32em" textAnchor="end">{compact(t)}</text>
            </g>
          ))}

          {years.map((yr, i) => (
            <g key={yr}>
              {arms[i].exports.segments.map((seg) => {
                const h = Math.max(len(seg.end - seg.start) - GAP, 0.75)
                return <path key={`e-${seg.key}`} fill={seg.color}
                  opacity={tip && tip.content.title !== String(yr) ? 0.45 : 1}
                  d={capped(x(yr), center - len(seg.end), x.thickness, h, 4, 'up')} />
              })}
              {arms[i].imports.segments.map((seg) => {
                const h = Math.max(len(seg.end - seg.start) - GAP, 0.75)
                return <path key={`i-${seg.key}`} fill={seg.color}
                  opacity={tip && tip.content.title !== String(yr) ? 0.45 : 1}
                  d={capped(x(yr), center + len(seg.start), x.thickness, h, 4, 'down')} />
              })}
            </g>
          ))}

          <line className="baseline" x1={M.left} x2={M.left + plotW} y1={center} y2={center} />

          {/* Arm labels live in the left margin, clear of the year ticks. */}
          {showUpAxis && (
            <text className="arm-label" transform={`translate(14 ${center - upArm / 2}) rotate(-90)`}
                  textAnchor="middle">Exports</text>
          )}
          {showDownAxis && (
            <text className="arm-label" transform={`translate(14 ${center + downArm / 2}) rotate(-90)`}
                  textAnchor="middle">Imports</text>
          )}
          {years.map((yr) => (
            <text key={`xl-${yr}`} className="tick" x={x.center(yr)} y={height - 8} textAnchor="middle">
              {yr}
            </text>
          ))}

          {years.map((yr, i) => (
            <rect
              key={`hit-${yr}`}
              className="hit"
              x={x.center(yr) - x.step / 2} y={M.top} width={x.step} height={plotH}
              onPointerMove={(e) => show(e, {
                title: String(yr),
                rows: [
                  ...arms[i].exports.segments.slice().reverse()
                    .map((s) => ({ label: `${s.label} · exported`, value: s.value, color: s.color })),
                  ...arms[i].imports.segments.slice().reverse()
                    .map((s) => ({ label: `${s.label} · imported`, value: s.value, color: s.color })),
                ],
              })}
              onPointerLeave={hide}
            />
          ))}
        </svg>
      )}

      {/* When one side is too small to carry an axis, say so rather than
          leaving an unexplained sliver under the line. */}
      {!showDownAxis && (
        <p className="plot-note">
          {peakImports > 0
            ? `Imports peak at ${compact(peakImports)} t — too small to show against exports on a shared scale.`
            : 'No imports recorded for this selection.'}
        </p>
      )}

      <Tooltip tip={tip} />
    </div>
  )
}
