import { availableSubregions, availableIntermediates, availableCountries } from '../api'
import { toCountryOptions, toOptions } from '../countries'
import Combobox from './Combobox'

/**
 * The geographic cascade, in one row above everything it scopes — region >
 * sub-region > intermediate region > country, as in the original dashboard.
 * Choosing an upstream value clears everything downstream of it.
 */
export default function GeoRow({ meta, filters, setFilters }) {
  const { hierarchy, regions } = meta

  const subregions = availableSubregions(hierarchy, filters.region)
  const intermediates = availableIntermediates(hierarchy, filters.region, filters.subregion)
  const countries = availableCountries(
    hierarchy, filters.region, filters.subregion, filters.intermediate,
  )

  return (
    <div className="geo-row">
      <Combobox
        label="Region" value={filters.region} options={toOptions(regions)}
        onChange={(v) => setFilters({ ...filters, region: v, subregion: null, intermediate: null, country: null })}
      />
      <Combobox
        label="Sub-region" value={filters.subregion} options={toOptions(subregions)}
        onChange={(v) => setFilters({ ...filters, subregion: v, intermediate: null, country: null })}
      />
      <Combobox
        label="Intermediate region" value={filters.intermediate} options={toOptions(intermediates)}
        onChange={(v) => setFilters({ ...filters, intermediate: v, country: null })}
      />
      <Combobox
        label="Country" value={filters.country} options={toCountryOptions(countries)}
        onChange={(v) => setFilters({ ...filters, country: v })}
      />
    </div>
  )
}
