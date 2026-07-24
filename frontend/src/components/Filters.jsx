import {
  availableSubregions,
  availableIntermediates,
  availableCountries,
} from '../api'
import { toCountryOptions, toOptions } from '../countries'
import Combobox from './Combobox'

// Show refined lead ("New Lead") first — it's the primary thing this tool tracks.
const CATEGORY_PRIORITY = { 'New Lead': 0 }
const orderCategories = (categories) =>
  [...categories].sort(
    (a, b) => (CATEGORY_PRIORITY[a.category] ?? 1) - (CATEGORY_PRIORITY[b.category] ?? 1),
  )

// Sidebar: product checklist, year range, geo cascade, and download.
export default function Filters({ meta, filters, setFilters, onDownload }) {
  const { hierarchy, regions, categories, year_min, year_max } = meta

  const subregions = availableSubregions(hierarchy, filters.region)
  const intermediates = availableIntermediates(hierarchy, filters.region, filters.subregion)
  const countries = availableCountries(
    hierarchy, filters.region, filters.subregion, filters.intermediate,
  )

  const allCodes = categories.flatMap((c) => c.products.map((p) => p.hs_code))
  const selected = filters.products ?? allCodes

  function toggleProduct(code) {
    const set = new Set(selected)
    set.has(code) ? set.delete(code) : set.add(code)
    // Keep config order stable so the stacking order stays consistent.
    setFilters({ ...filters, products: allCodes.filter((c) => set.has(c)) })
  }

  // Cascading selects clear everything downstream when an upstream value changes.
  const setRegion = (v) =>
    setFilters({ ...filters, region: v, subregion: null, intermediate: null, country: null })
  const setSubregion = (v) =>
    setFilters({ ...filters, subregion: v, intermediate: null, country: null })
  const setIntermediate = (v) =>
    setFilters({ ...filters, intermediate: v, country: null })
  const setCountry = (v) => setFilters({ ...filters, country: v })

  const [start, end] = filters.years ?? [year_min, year_max]

  return (
    <aside className="filters">
      <section className="filter-group">
        <h3>Products</h3>
        <p className="filter-hint">Defaults to refined lead. Check more boxes for other products.</p>
        {orderCategories(categories).map((cat) => (
          <div key={cat.category} className="product-category">
            <div className="product-category-title" style={{ color: cat.base_color }}>
              {cat.category}
            </div>
            {cat.products.map((p) => (
              <label key={p.hs_code} className="checkbox-row">
                <input
                  type="checkbox"
                  checked={selected.includes(p.hs_code)}
                  onChange={() => toggleProduct(p.hs_code)}
                />
                <span className="swatch" style={{ background: p.color }} />
                <span className="checkbox-label">{p.hs_code} · {p.name}</span>
              </label>
            ))}
          </div>
        ))}
        {selected.length === 0 && (
          <p className="warn">Select at least one product to see data.</p>
        )}
      </section>

      <section className="filter-group">
        <h3>Year Range</h3>
        <div className="year-range">
          <span>{start}</span>
          <div className="sliders">
            <input
              type="range" min={year_min} max={year_max} value={start}
              onChange={(e) => setFilters({ ...filters, years: [Math.min(+e.target.value, end), end] })}
            />
            <input
              type="range" min={year_min} max={year_max} value={end}
              onChange={(e) => setFilters({ ...filters, years: [start, Math.max(+e.target.value, start)] })}
            />
          </div>
          <span>{end}</span>
        </div>
      </section>

      <section className="filter-group">
        <h3>Geography</h3>
        <Combobox label="Region" value={filters.region} options={toOptions(regions)} onChange={setRegion} />
        <Combobox label="Sub-region" value={filters.subregion} options={toOptions(subregions)} onChange={setSubregion} />
        <Combobox label="Intermediate Region" value={filters.intermediate} options={toOptions(intermediates)} onChange={setIntermediate} />
        <Combobox label="Country" value={filters.country} options={toCountryOptions(countries)} onChange={setCountry} />
      </section>

      <section className="filter-group">
        <button className="download-btn" type="button" onClick={onDownload}>
          ⬇ Download Filtered Data
        </button>
      </section>
    </aside>
  )
}
