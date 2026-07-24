// Renders the HS-code glossary from /api/meta (mirrors app.py's bottom section).
export default function ProductDefinitions({ categories }) {
  return (
    <section className="definitions" id="product-definitions">
      <h2>Product Definitions</h2>
      <p>
        Our analysis is based on{' '}
        <a href="https://www.wcotradetools.org/en/harmonized-system" target="_blank" rel="noreferrer">
          Harmonized System (HS) codes
        </a>
        , a global standard for classifying traded goods.
      </p>
      {categories.map((cat) => (
        <div key={cat.category} className="definition-category">
          <h3 style={{ color: cat.base_color }}>{cat.category}</h3>
          {cat.products.map((p) => (
            <p key={p.hs_code}>
              <strong>{p.hs_code} — {p.name}</strong>
              <br />
              {p.definition}
            </p>
          ))}
        </div>
      ))}
    </section>
  )
}
