import { useState } from 'react'
import RangeSlider from './RangeSlider'

// Sidebar: product checklist, year range, and the CSV download.
// Geography lives in its own row above the charts (see GeoRow), as it did in
// the original dashboard.
export default function Filters({ meta, filters, setFilters, onDownload }) {
  const [open, setOpen] = useState(false)
  const { categories, year_min, year_max } = meta

  const allCodes = categories.flatMap((c) => c.products.map((p) => p.hs_code))
  const selected = filters.products ?? allCodes

  function toggleProduct(code) {
    const set = new Set(selected)
    set.has(code) ? set.delete(code) : set.add(code)
    // Keep config order stable so the stacking order stays consistent.
    setFilters({ ...filters, products: allCodes.filter((c) => set.has(c)) })
  }

  const [start, end] = filters.years ?? [year_min, year_max]
  const setYears = (a, b) => setFilters({ ...filters, years: [a, b] })
  const productSummary = `${selected.length} product${selected.length === 1 ? '' : 's'}`

  return (
    <aside className={open ? 'sidebar filters-open' : 'sidebar'}>
      <button
        className="filter-toggle"
        type="button"
        aria-expanded={open}
        aria-controls="filter-panel"
        onClick={() => setOpen((value) => !value)}
      >
        <span>
          <span className="filter-toggle-title">Filters</span>
          <span className="filter-summary">{productSummary} · {start}–{end}</span>
        </span>
        <span className="filter-toggle-action" aria-hidden="true">{open ? 'Close' : 'Edit'}</span>
      </button>

      <div className="sidebar-panel" id="filter-panel">
        <section className="group">
          <h2>Products</h2>
          <p className="hint">Refined lead is selected by default. Add categories to widen the view.</p>

          {categories.map((cat) => (
            <div key={cat.category} className="product-group">
              <p className="group-title">{cat.category}</p>
              {cat.products.map((p) => (
                <label key={p.hs_code} className="check">
                  <input
                    type="checkbox"
                    checked={selected.includes(p.hs_code)}
                    onChange={() => toggleProduct(p.hs_code)}
                  />
                  <span className="swatch" style={{ background: p.color }} aria-hidden="true" />
                  <span className="check-code">{p.hs_code}</span>
                  <span className="check-name">{p.name}</span>
                </label>
              ))}
            </div>
          ))}

          {selected.length === 0 && <p className="hint warn">Select at least one product.</p>}
        </section>

        <section className="group">
          <h2>Years</h2>
          <RangeSlider
            min={year_min}
            max={year_max}
            start={start}
            end={end}
            onChange={setYears}
          />
        </section>

        <section className="group download-group">
          <button className="btn btn-solid" type="button" onClick={onDownload}>
            Download filtered data
          </button>
          <p className="hint">CSV of every row behind the current selection.</p>
        </section>
      </div>
    </aside>
  )
}
