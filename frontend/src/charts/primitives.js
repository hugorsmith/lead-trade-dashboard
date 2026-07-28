// Chart primitives: scales, ticks, formatters and path helpers.
//
// Small enough to own outright. Replacing Plotly (4.9 MB) with hand-built SVG
// means the marks obey the house specs exactly — capped bar thickness, a 2 px
// surface gap between touching fills, and a rounded data-end that stays square
// at the baseline — none of which a charting library exposes cleanly.

/** Continuous scale from a [0, max] domain onto a pixel range. */
export function linear(maxValue, [r0, r1]) {
  const max = maxValue > 0 ? maxValue : 1
  const scale = (v) => r0 + ((r1 - r0) * v) / max
  scale.max = max
  return scale
}

/**
 * Ordinal band scale. `maxBand` caps how thick a mark may get so a chart with
 * few categories doesn't render slabs — the leftover becomes air.
 */
export function band(domain, [r0, r1], { padding = 0.28, maxBand = 24 } = {}) {
  const n = Math.max(domain.length, 1)
  const step = (r1 - r0) / n
  const thickness = Math.min(step * (1 - padding), maxBand)
  const index = new Map(domain.map((d, i) => [d, i]))

  const scale = (d) => {
    const i = index.get(d)
    return i === undefined ? r0 : r0 + i * step + (step - thickness) / 2
  }
  scale.thickness = Math.max(thickness, 1)
  scale.step = step
  /** Centre of a band — for axis labels and hover bands. */
  scale.center = (d) => scale(d) + scale.thickness / 2
  return scale
}

/** Round a domain max up to a clean tick interval and return the tick values. */
export function ticks(maxValue, count = 5) {
  if (!(maxValue > 0)) return { max: 1, values: [0, 1] }
  const raw = maxValue / count
  const mag = 10 ** Math.floor(Math.log10(raw))
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw) ?? mag * 10
  const max = Math.ceil(maxValue / step) * step
  const values = []
  for (let v = 0; v <= max + step / 2; v += step) values.push(v)
  return { max, values }
}

// --- Formatting -----------------------------------------------------------

/** Compact tonnage for axis ticks and dense labels: 1.2M, 51.4k, 940. */
export function compact(n) {
  const abs = Math.abs(n)
  if (abs === 0) return '0'
  if (abs >= 1e9) return `${(n / 1e9).toFixed(abs >= 1e10 ? 0 : 1)}B`
  if (abs >= 1e6) return `${(n / 1e6).toFixed(abs >= 1e7 ? 0 : 1)}M`
  if (abs >= 1e3) return `${(n / 1e3).toFixed(abs >= 1e4 ? 0 : 1)}k`
  return abs >= 10 ? n.toFixed(0) : n.toFixed(abs >= 1 ? 1 : 2)
}

/** Full precision with thousands separators, for tooltips and tables. */
export const full = (n) =>
  n.toLocaleString(undefined, { maximumFractionDigits: n >= 100 ? 0 : 2 })

/**
 * Bar-tip labels. Whole tonnes once a value is big enough to warrant them, so a
 * ranked column doesn't mix "147,783" with "65.49" and read as noise.
 */
export const label = (n) =>
  n.toLocaleString(undefined, { maximumFractionDigits: n >= 10 ? 0 : 1 })

// --- Geometry -------------------------------------------------------------

/** The 2 px of surface that separates touching fills. */
export const GAP = 2

/**
 * A rect whose far end is rounded and whose baseline end stays square.
 * `side` is the direction the mark grows: 'up' for columns, 'right' for bars.
 */
export function capped(x, y, w, h, r = 4, side = 'up') {
  const rad = Math.max(0, Math.min(r, side === 'up' ? w / 2 : h / 2, side === 'up' ? h : w))
  if (rad <= 0.5) return `M${x},${y}h${w}v${h}h${-w}Z`

  if (side === 'up') {
    // y is the top of the mark; it grows downward to the baseline at y + h.
    return `M${x},${y + rad}a${rad},${rad} 0 0 1 ${rad},${-rad}h${w - 2 * rad}` +
      `a${rad},${rad} 0 0 1 ${rad},${rad}v${h - rad}h${-w}Z`
  }
  if (side === 'down') {
    // Square at the baseline on top, rounded at the bottom data-end.
    return `M${x},${y}h${w}v${h - rad}a${rad},${rad} 0 0 1 ${-rad},${rad}h${-(w - 2 * rad)}` +
      `a${rad},${rad} 0 0 1 ${-rad},${-rad}Z`
  }
  // Bars grow rightward from a baseline at x.
  return `M${x},${y}h${w - rad}a${rad},${rad} 0 0 1 ${rad},${rad}v${h - 2 * rad}` +
    `a${rad},${rad} 0 0 1 ${-rad},${rad}h${-(w - rad)}Z`
}

/**
 * Turn a series of values into cumulative [start, end] spans in data units,
 * dropping empties and marking the outermost one (the only segment whose
 * data-end is rounded). Each chart maps the spans to pixels itself, since the
 * axis direction differs between columns and bars.
 */
export function stack(items) {
  const out = []
  let cursor = 0
  for (const item of items) {
    if (!(item.value > 0)) continue
    out.push({ ...item, start: cursor, end: cursor + item.value })
    cursor += item.value
  }
  if (out.length) out[out.length - 1].outermost = true
  return { segments: out, total: cursor }
}
