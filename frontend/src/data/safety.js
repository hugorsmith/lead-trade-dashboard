// Curated "safety of source" data for the US refined-lead import view.
// Port of backend/safety.py.
//
// Countries flagged here have documented hazards from informal / unsafe used
// lead-acid battery (ULAB) recycling. Their bars and labels render in red on the
// safety view, with the source links shown alongside.
//
// NOTE (editorial): the flagged list and citations below are a starting point
// and should be reviewed/expanded by the project owner. Add or replace links
// with the specific reports you want to cite.

/** Highlight colour used for flagged countries (bars + labels + panel). */
export const FLAG_COLOR = '#ef4444'

const WHO = {
  title: 'WHO — Lead poisoning (ULAB recycling as a major source)',
  url: 'https://www.who.int/news-room/fact-sheets/detail/lead-poisoning-and-health',
}
const PURE_EARTH = {
  title: 'Pure Earth — Used Lead-Acid Battery (ULAB) recycling',
  url: 'https://www.pureearth.org/',
}

/** Country name (as it appears in the trade data) -> list of source links. */
export const UNSAFE_SOURCES = {
  Nigeria: [WHO, PURE_EARTH],
  Ghana: [WHO, PURE_EARTH],
  India: [WHO, PURE_EARTH],
}

/** Set of country names flagged for unsafe ULAB recycling. */
export const flaggedCountries = () => new Set(Object.keys(UNSAFE_SOURCES))
