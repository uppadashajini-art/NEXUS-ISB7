
function CompetitorCard({ competitor }) {
  const {
    name,
    url,
    target_customers,
    key_features = [],
    strengths = [],
    weaknesses = [],
  } = competitor;

  return (
    <div className="competitor-card">
      <h3>{name}</h3>

      {url && (
        <p>
          <a href={url} target="_blank" rel="noopener noreferrer">
            {url}
          </a>
        </p>
      )}

      {target_customers && (
        <p>
          <strong>Target Customers:</strong> {target_customers}
        </p>
      )}

      {key_features.length > 0 && (
        <>
          <h4>Key Features</h4>
          <ul>
            {key_features.map((f, i) => (
              <li key={i}>{f}</li>
            ))}
          </ul>
        </>
      )}

      {strengths.length > 0 && (
        <>
          <h4>Strengths</h4>
          <ul>
            {strengths.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </>
      )}

      {weaknesses.length > 0 && (
        <>
          <h4>Weaknesses</h4>
          <ul>
            {weaknesses.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

export default function CompetitorAnalysis({ data }) {
  if (!data) return null;

  const { direct_competitors = [], indirect_competitors = [] } = data;

  return (
    <section className="analysis-card">
      <h2>Competitor Analysis</h2>

      {direct_competitors.length > 0 && (
        <div className="competitor-group">
          <h3>Direct Competitors</h3>
          {direct_competitors.map((c, i) => (
            <CompetitorCard competitor={c} key={i} />
          ))}
        </div>
      )}

      {indirect_competitors.length > 0 && (
        <div className="competitor-group">
          <h3>Indirect Competitors</h3>
          {indirect_competitors.map((c, i) => (
            <CompetitorCard competitor={c} key={i} />
          ))}
        </div>
      )}
    </section>
  );
}