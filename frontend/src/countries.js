// Country display labels + search aliases.
//
// The trade data uses short/official names (e.g. "USA", "Rep. of Korea"). These
// maps let a user find a country by common names — typing "united" or "america"
// surfaces USA — while the value sent to the backend stays the exact data name.

// Optional friendlier display label (value stays the data name).
const DISPLAY = {
  USA: 'United States (USA)',
  'Rep. of Korea': 'South Korea (Rep. of Korea)',
  "Dem. People's Rep. of Korea": 'North Korea (DPRK)',
  'Russian Federation': 'Russia',
  'Viet Nam': 'Vietnam',
  'Rep. of Moldova': 'Moldova',
  'United Rep. of Tanzania': 'Tanzania',
  "Lao People's Dem. Rep.": 'Laos',
  'Dem. Rep. of the Congo': 'DR Congo',
  'China, Hong Kong SAR': 'Hong Kong',
  'China, Macao SAR': 'Macao',
  'Bolivia (Plurinational State of)': 'Bolivia',
}

// Extra search terms (synonyms) beyond the name/display text itself.
const ALIASES = {
  USA: ['united states', 'us', 'u.s.', 'u.s.a', 'america', 'united states of america'],
  'United Kingdom': ['uk', 'u.k.', 'britain', 'great britain', 'england'],
  'Rep. of Korea': ['south korea', 'korea', 'republic of korea'],
  "Dem. People's Rep. of Korea": ['north korea', 'dprk'],
  'Russian Federation': ['russia'],
  'Viet Nam': ['vietnam'],
  Türkiye: ['turkey', 'turkiye'],
  "Côte d'Ivoire": ['ivory coast', 'cote divoire', "cote d'ivoire"],
  Czechia: ['czech republic', 'czech'],
  'United Arab Emirates': ['uae', 'emirates'],
  'United Rep. of Tanzania': ['tanzania'],
  "Lao People's Dem. Rep.": ['laos', 'lao'],
  'Rep. of Moldova': ['moldova'],
  'Dem. Rep. of the Congo': ['dr congo', 'drc', 'democratic republic of congo', 'congo kinshasa'],
  'China, Hong Kong SAR': ['hong kong'],
  'China, Macao SAR': ['macao', 'macau'],
  'Bolivia (Plurinational State of)': ['bolivia'],
  'Central African Rep.': ['central african republic', 'car'],
  'Dominican Rep.': ['dominican republic'],
}

export function countryLabel(name) {
  return DISPLAY[name] ?? name
}

// Build combobox options: value = data name, label = display, search = haystack.
export function toCountryOptions(names) {
  return names.map((name) => {
    const label = countryLabel(name)
    const aliases = ALIASES[name] ?? []
    const search = [name, label, ...aliases].join(' ').toLowerCase()
    return { value: name, label, search }
  })
}

// Plain string options (regions, subregions, ...) — search on the text itself.
export function toOptions(values) {
  return values.map((v) => ({ value: v, label: v, search: String(v).toLowerCase() }))
}
