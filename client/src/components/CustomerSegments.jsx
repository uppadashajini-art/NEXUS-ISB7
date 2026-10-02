import React from "react";

function renderSafe(val, fallback = "") {
  if (val === null || val === undefined) return fallback;
  if (typeof val === "string") return val;
  if (typeof val === "number" || typeof val === "boolean") return String(val);
  if (Array.isArray(val)) return val.map((v) => renderSafe(v)).filter(Boolean).join(", ");
  if (typeof val === "object") {
    return val.pain || val.need || val.text || val.name || val.point || JSON.stringify(val);
  }
  return String(val);
}

export default function CustomerSegments({ segments }) {
  if (!segments || segments.length === 0) return null;

  return (
    <section className="analysis-card customer-segments-card">
      <div className="section-title-wrap">
        <span className="card-mini-badge" style={{ background: "linear-gradient(135deg, rgba(255,199,44,0.15), rgba(255,138,31,0.15))", color: "#FFC72C", border: "1px solid rgba(255,199,44,0.3)" }}>
          TARGET AUDIENCE
        </span>
        <h2>Customer Segments</h2>
      </div>

      <div className="customer-segments-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "16px", marginTop: "16px" }}>
        {segments.map((seg, i) => {
          const segTitle = renderSafe(seg.segment || seg.name || `Segment ${i + 1}`);
          const needs = Array.isArray(seg.needs) ? seg.needs : [];
          const painPoints = Array.isArray(seg.pain_points) ? seg.pain_points : [];

          return (
            <div className="segment-block gtm-card" key={i} style={{ background: "rgba(255, 255, 255, 0.025)", border: "1px solid rgba(255, 255, 255, 0.07)", borderRadius: "12px", padding: "20px", transition: "all 0.2s ease" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "14px" }}>
                <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: "linear-gradient(135deg, rgba(255,199,44,0.2), rgba(255,138,31,0.2))", color: "#FFC72C", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700 }}>
                  👥
                </div>
                <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700, color: "#f5f1e8" }}>{segTitle}</h3>
              </div>

              {needs.length > 0 && (
                <div style={{ marginBottom: "14px" }}>
                  <h4 style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#FFC72C", margin: "0 0 6px 0" }}>
                    Needs
                  </h4>
                  <ul style={{ margin: 0, paddingLeft: "18px", fontSize: "0.85rem", color: "#d1c7b7", lineHeight: "1.5" }}>
                    {needs.map((need, j) => (
                      <li key={j} style={{ marginBottom: "4px" }}>{renderSafe(need)}</li>
                    ))}
                  </ul>
                </div>
              )}

              {painPoints.length > 0 && (
                <div>
                  <h4 style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#f87171", margin: "0 0 6px 0" }}>
                    Pain Points
                  </h4>
                  <ul style={{ margin: 0, paddingLeft: "18px", fontSize: "0.85rem", color: "#d1c7b7", lineHeight: "1.5" }}>
                    {painPoints.map((point, j) => {
                      const text = renderSafe(point);
                      const severity = typeof point === "object" && point.severity ? point.severity : null;
                      return (
                        <li key={j} style={{ marginBottom: "4px" }}>
                          <span>{text}</span>
                          {severity && (
                            <span style={{ marginLeft: "8px", fontSize: "0.7rem", padding: "1px 6px", borderRadius: "4px", background: "rgba(239,68,68,0.15)", color: "#f87171", fontWeight: 600 }}>
                              {severity}
                            </span>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}