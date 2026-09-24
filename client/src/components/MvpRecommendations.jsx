import React from "react";

export default function MvpRecommendations({ mvpData }) {
  if (!mvpData) return null;

  const {
    must_have = [],
    should_have = [],
    could_have = [],
    future_features = []
  } = mvpData;

  const totalFeatures = must_have.length + should_have.length + could_have.length + future_features.length;
  if (totalFeatures === 0) return null;

  const tiers = [
    { title: "Must-Have (Core MVP)", items: must_have, badge: "P0 • Launch Critical", color: "var(--gold)", bg: "rgba(232, 199, 123, 0.08)", border: "rgba(232, 199, 123, 0.3)" },
    { title: "Should-Have (Fast Follow)", items: should_have, badge: "P1 • Post-Launch", color: "#64b5f6", bg: "rgba(100, 181, 246, 0.08)", border: "rgba(100, 181, 246, 0.3)" },
    { title: "Could-Have (Enhancements)", items: could_have, badge: "P2 • Expansion", color: "var(--success)", bg: "rgba(159, 214, 164, 0.08)", border: "rgba(159, 214, 164, 0.3)" },
    { title: "Future Roadmap", items: future_features, badge: "P3 • Scale Phase", color: "var(--secondary)", bg: "rgba(255, 255, 255, 0.04)", border: "var(--border)" }
  ];

  return (
    <section className="analysis-card mvp-recommendations-card" style={{ marginTop: "24px" }}>
      <div className="section-header-row" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>
          <span className="mini-label" style={{ color: "var(--gold)", fontSize: "0.75rem", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase" }}>
            PRODUCT EXECUTION ROADMAP
          </span>
          <h2 style={{ margin: "4px 0 0", fontSize: "1.4rem", color: "var(--text)" }}>MVP Feature Recommendations</h2>
        </div>
        <div style={{ background: "rgba(232, 199, 123, 0.1)", border: "1px solid var(--border-light)", padding: "6px 14px", borderRadius: "12px", color: "var(--gold)", fontSize: "0.85rem", fontWeight: 600 }}>
          {totalFeatures} Prioritized Features
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        {tiers.map((tier, tIdx) => {
          if (!tier.items || tier.items.length === 0) return null;
          return (
            <div key={tIdx} style={{ background: tier.bg, border: `1px solid ${tier.border}`, borderRadius: "var(--radius-md)", padding: "20px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
                <h3 style={{ margin: 0, fontSize: "1.1rem", color: tier.color, fontWeight: 700 }}>
                  {tier.title}
                </h3>
                <span style={{ fontSize: "0.75rem", fontWeight: 700, color: tier.color, letterSpacing: "0.5px", textTransform: "uppercase" }}>
                  {tier.badge}
                </span>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "12px" }}>
                {tier.items.map((feat, fIdx) => (
                  <div key={fIdx} style={{ background: "var(--card)", border: "1px solid var(--border)", borderRadius: "10px", padding: "14px", display: "flex", flexDirection: "column", gap: "8px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "8px" }}>
                      <strong style={{ color: "var(--text)", fontSize: "0.95rem" }}>
                        {feat.feature}
                      </strong>
                    </div>
                    {feat.reason && (
                      <p style={{ margin: 0, color: "var(--secondary)", fontSize: "0.85rem", lineHeight: "1.45" }}>
                        {feat.reason}
                      </p>
                    )}
                    <div style={{ display: "flex", gap: "8px", marginTop: "auto", paddingTop: "6px" }}>
                      {feat.customer_value && (
                        <span style={{ background: "rgba(159, 214, 164, 0.12)", color: "var(--success)", padding: "2px 8px", borderRadius: "6px", fontSize: "0.72rem", fontWeight: 600 }}>
                          Value: {feat.customer_value}
                        </span>
                      )}
                      {feat.complexity && (
                        <span style={{ background: "rgba(255, 180, 167, 0.12)", color: "var(--coral-light)", padding: "2px 8px", borderRadius: "6px", fontSize: "0.72rem", fontWeight: 600 }}>
                          Complexity: {feat.complexity}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
