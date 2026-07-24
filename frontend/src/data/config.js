// Product lookups, derived from meta.json at load time.
//
// The HS categories/colours/labels/definitions still live in src/config.py and
// are baked into meta.json by scripts/export_data.py, so there is exactly one
// source of truth for them. This module just turns that payload into the maps
// the aggregation and figure code needs.

/**
 * Build product lookup tables from meta.categories.
 *
 * @returns {{
 *   allCodes: string[],          // every HS code, in config order
 *   colors: Record<string,string>,   // hs code -> bar colour
 *   labels: Record<string,string>,   // hs code -> "780110 - Refined lead…"
 *   toCategory: Record<string,string>, // hs code -> category name
 *   order: Record<string,number>,    // hs code -> position in config order
 *   categories: string[],            // category names, in config order
 *   categoryColor: Record<string,string>, // category -> base colour
 * }}
 */
export function buildProductIndex(categories) {
  const allCodes = []
  const colors = {}
  const labels = {}
  const toCategory = {}
  const order = {}
  const names = []
  const categoryColor = {}

  for (const cat of categories) {
    names.push(cat.category)
    categoryColor[cat.category] = cat.base_color
    for (const p of cat.products) {
      order[p.hs_code] = allCodes.length
      allCodes.push(p.hs_code)
      colors[p.hs_code] = p.color
      labels[p.hs_code] = p.label
      toCategory[p.hs_code] = cat.category
    }
  }

  return { allCodes, colors, labels, toCategory, order, categories: names, categoryColor }
}
