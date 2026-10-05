// Place this file at: client/src/components/MvpRecommendations.jsx
//
// Styled to match GtmStrategy.jsx's .gtm-card / .pain-item design language.

function FeatureGroup({ title, icon, features }) {
  if (!features || features.length === 0) return null;
  return (
    <div className="gtm-card" style={{ marginBottom: "16px" }}>
      <div className="gtm-card-header">
        <div className="gtm-card-icon">{icon}</div>
        <h3 className="gtm-card-title">{title}</h3>
      </div>
      {features.map((f, i) => (
        <div key={i} className="pain-item">
          <span className="pain-source-tag">{f.complexity || "Feature"}</span>
          <p className="pain-desc pain-feature-title" style={{ fontWeight: 700 }}>{f.feature}</p>
          {f.reason && (
            <p className="pain-desc pain-reason" style={{ margin: "4px 0 0 0", color: "#b8b2a7" }}>
              {f.reason}
            </p>
          )}
          {f.customer_value && (
            <p style={{ margin: "6px 0 0 0", fontSize: "0.78rem", color: "#e28743" }}>
              Customer Value: {f.customer_value}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}

export default function MvpRecommendations({ data }) {
  if (!data) return null;

  const { must_have = [], should_have = [], could_have = [], future_features = [] } = data;

  return (
    <section className="analysis-card">
      <h2>MVP Recommendations</h2>

      <FeatureGroup title="Must Have" icon="🚀" features={must_have} />
      <FeatureGroup title="Should Have" icon="⭐" features={should_have} />
      <FeatureGroup title="Could Have" icon="💡" features={could_have} />
      <FeatureGroup title="Future Features" icon="🔮" features={future_features} />

      <style>{`
        .gtm-card {
          background: rgba(255, 255, 255, 0.025);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 14px;
          padding: 22px;
          transition: all 0.25s ease;
        }
        .gtm-card:hover {
          border-color: rgba(226, 135, 67, 0.25);
          background: rgba(255, 255, 255, 0.04);
        }
        .gtm-card-header {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 16px;
        }
        .gtm-card-icon {
          width: 32px;
          height: 32px;
          border-radius: 8px;
          background: rgba(226, 135, 67, 0.15);
          color: #e28743;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 0.95rem;
        }
        .gtm-card-title {
          font-size: 1.1rem;
          font-weight: 600;
          margin: 0;
          color: #f5f1e8;
        }
        .pain-item {
          background: rgba(0, 0, 0, 0.25);
          border-left: 3px solid #e28743;
          border-radius: 0 8px 8px 0;
          padding: 12px 14px;
          margin-bottom: 10px;
        }
        .pain-source-tag {
          font-size: 0.68rem;
          font-weight: 700;
          text-transform: uppercase;
          background: rgba(255, 255, 255, 0.06);
          padding: 2px 7px;
          border-radius: 4px;
          color: #e28743;
          margin-right: 8px;
        }
        .pain-desc {
          font-size: 0.88rem;
          color: #e6e0d4;
          margin: 6px 0 2px 0;
          line-height: 1.4;
        }

        /* -----------------------------------------------
           LIGHT THEME OVERRIDES
        ----------------------------------------------- */
        [data-theme="light"] .gtm-card {
          background: #ffffff;
          border-color: rgba(0, 0, 0, 0.08);
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }
        [data-theme="light"] .gtm-card:hover {
          border-color: rgba(226, 135, 67, 0.35);
          background: #faf9f5;
        }
        [data-theme="light"] .gtm-card-title {
          color: #18181b;
        }
        [data-theme="light"] .pain-item {
          background: #f8f9fb;
          border-color: rgba(0, 0, 0, 0.06);
          border-left: 3px solid #e28743;
        }
        [data-theme="light"] .pain-feature-title {
          color: #18181b !important;
        }
        [data-theme="light"] .pain-reason {
          color: #52525b !important;
        }
        [data-theme="light"] .pain-desc {
          color: #27272a;
        }
        [data-theme="light"] .pain-source-tag {
          background: rgba(226, 135, 67, 0.1);
          color: #c25e1a;
        }
      `}</style>
    </section>
  );
}