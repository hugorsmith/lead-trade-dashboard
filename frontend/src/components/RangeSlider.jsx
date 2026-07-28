import { useId } from 'react'

/**
 * A dual-handle range on a single track: the selected span is filled between the
 * two handles, so it reads as one range instead of two disconnected sliders.
 *
 * Built from two overlaid native range inputs (there is no native dual-thumb
 * input). Each input is pointer-transparent except its thumb, so both handles
 * stay grabbable where they don't overlap; the onChange clamps keep them from
 * crossing. The handle sitting at the higher value is raised so the two can
 * still be pulled apart when they meet.
 */
export default function RangeSlider({ min, max, start, end, onChange, format = String }) {
  const id = useId()
  const span = max - min || 1
  const pct = (v) => ((v - min) / span) * 100

  // When the handles meet at the top of the range, lift the start handle so it
  // isn't buried under the end handle and can be dragged back down.
  const startOnTop = start >= max

  return (
    <div className="range-slider">
      <div className="range-readout">
        <span className="range-year">{format(start)}</span>
        <span className="range-to" aria-hidden="true">–</span>
        <span className="range-year">{format(end)}</span>
      </div>

      <div className="range-track">
        <div className="range-rail" />
        <div
          className="range-sel"
          style={{ left: `${pct(start)}%`, right: `${100 - pct(end)}%` }}
        />
        <input
          type="range" min={min} max={max} value={start}
          style={{ zIndex: startOnTop ? 4 : 3 }}
          aria-label="First year"
          aria-describedby={id}
          onChange={(e) => onChange(Math.min(+e.target.value, end), end)}
        />
        <input
          type="range" min={min} max={max} value={end}
          aria-label="Last year"
          aria-describedby={id}
          onChange={(e) => onChange(start, Math.max(+e.target.value, start))}
        />
      </div>

      <div className="range-bounds" id={id}>
        <span>{format(min)}</span>
        <span>{format(max)}</span>
      </div>
    </div>
  )
}
