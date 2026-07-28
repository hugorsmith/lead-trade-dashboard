// The HS-code glossary, as in the original dashboard's closing section.
//
// Category headings carry a colour swatch rather than coloured text: several
// palette slots are too light to read as type on white, and identity is meant
// to come from a mark beside the label, never from tinting the label itself.
export default function ProductDefinitions({ categories }) {
  return (
    <section className="definitions" id="product-definitions">
      <h2>What the codes mean</h2>
      <p className="hint">
        Trade is classified by{' '}
        <a href="https://www.wcotradetools.org/en/harmonized-system" target="_blank" rel="noreferrer">
          Harmonized System (HS) codes
        </a>
        , the global standard for describing traded goods.
      </p>

      <div className="definition-grid">
        {categories.map((cat) => (
          <div key={cat.category} className="definition-group">
            <h3>
              <span className="swatch" style={{ background: cat.base_color }} aria-hidden="true" />
              {cat.category}
            </h3>
            <dl>
              {cat.products.map((p) => (
                <div key={p.hs_code} className="definition">
                  <dt>
                    <span className="swatch sm" style={{ background: p.color }} aria-hidden="true" />
                    <span className="code">{p.hs_code}</span> {p.name}
                  </dt>
                  <dd>{p.definition}</dd>
                </div>
              ))}
            </dl>
          </div>
        ))}
      </div>
    </section>
  )
}
