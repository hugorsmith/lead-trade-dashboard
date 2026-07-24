// Sidebar: product checklist, year range, and the CSV download.
// Geography lives in its own row above the charts (see GeoRow), as it did in
// the original dashboard.
export default function Filters({ meta, filters, setFilters, onDownload }) {
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

  return (
    <aside className="sidebar">
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
        <div className="range">
          <output>{start}</output>
          <span className="range-dash" aria-hidden="true" />
          <output>{end}</output>
        </div>
        <label className="sr-only" htmlFor="year-from">First year</label>
        <input
          id="year-from" type="range" min={year_min} max={year_max} value={start}
          onChange={(e) => setYears(Math.min(+e.target.value, end), end)}
        />
        <label className="sr-only" htmlFor="year-to">Last year</label>
        <input
          id="year-to" type="range" min={year_min} max={year_max} value={end}
          onChange={(e) => setYears(start, Math.max(+e.target.value, start))}
        />
      </section>

      <section className="group">
        <button className="btn btn-solid" type="button" onClick={onDownload}>
          Download filtered data
        </button>
        <p className="hint">CSV of every row behind the current selection.</p>
      </section>
    </aside>
  )
}
