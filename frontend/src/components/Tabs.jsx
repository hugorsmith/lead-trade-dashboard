import { useState } from 'react'

export default function Tabs({ tabs }) {
  const [active, setActive] = useState(0)
  return (
    <div className="tabs">
      <div className="tab-bar" role="tablist">
        {tabs.map((t, i) => (
          <button
            key={t.label}
            role="tab"
            aria-selected={i === active}
            className={`tab ${i === active ? 'active' : ''}`}
            onClick={() => setActive(i)}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div className="tab-panel" role="tabpanel">
        {tabs[active].content}
      </div>
    </div>
  )
}
