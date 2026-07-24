import { useState, useRef, useEffect } from 'react'

// A searchable single-select. Options are { value, label, search }; `search` is
// a lowercased haystack that may include aliases (see countries.js).
export default function Combobox({ label, value, options, onChange, placeholder = 'All' }) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const ref = useRef(null)

  useEffect(() => {
    const onDocClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false)
        setQuery('')
      }
    }
    document.addEventListener('mousedown', onDocClick)
    return () => document.removeEventListener('mousedown', onDocClick)
  }, [])

  const selected = options.find((o) => o.value === value)
  const q = query.trim().toLowerCase()
  const filtered = q ? options.filter((o) => o.search.includes(q)) : options

  const pick = (v) => {
    onChange(v)
    setOpen(false)
    setQuery('')
  }

  return (
    <div className="combobox" ref={ref}>
      <span className="combobox-label">{label}</span>
      <div className={`combobox-control ${open ? 'open' : ''}`} onClick={() => setOpen(true)}>
        {open ? (
          <input
            autoFocus
            className="combobox-input"
            value={query}
            placeholder={selected ? selected.label : `Search ${label.toLowerCase()}…`}
            onChange={(e) => setQuery(e.target.value)}
          />
        ) : (
          <span className={`combobox-value ${selected ? '' : 'dim'}`}>
            {selected ? selected.label : placeholder}
          </span>
        )}
        {value ? (
          <button
            className="combobox-clear"
            title="Clear"
            onMouseDown={(e) => { e.stopPropagation(); pick(null) }}
          >
            ×
          </button>
        ) : (
          <span className="combobox-caret">▾</span>
        )}
      </div>
      {open && (
        <ul className="combobox-list" role="listbox">
          <li className={!value ? 'active' : ''} onMouseDown={() => pick(null)}>{placeholder}</li>
          {filtered.map((o) => (
            <li
              key={o.value}
              role="option"
              aria-selected={o.value === value}
              className={o.value === value ? 'active' : ''}
              onMouseDown={() => pick(o.value)}
            >
              {o.label}
            </li>
          ))}
          {filtered.length === 0 && <li className="empty">No matches</li>}
        </ul>
      )}
    </div>
  )
}
