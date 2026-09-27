function FeatureGroup({ title, features }) {
  if (!features || features.length === 0) return null;
  return (
    <div className="mvp-group">
      <h3>{title}</h3>
      {features.map((f, i) => (
        <div className="mvp-feature" key={i}>
          <strong>{f.feature}</strong>
          {f.reason && <p>{f.reason}</p>}
          <div className="mvp-meta">
            {f.customer_value && <span>Customer Value: {f.customer_value}</span>}
            {f.complexity && <span>Complexity: {f.complexity}</span>}
          </div>
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
      <FeatureGroup title="Must Have" features={must_have} />
      <FeatureGroup title="Should Have" features={should_have} />
      <FeatureGroup title="Could Have" features={could_have} />
      <FeatureGroup title="Future Features" features={future_features} />
    </section>
  );
}