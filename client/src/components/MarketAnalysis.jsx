export default function MarketAnalysis({ data }) {
  if (!data) return null;

  const {
    industry,
    market_opportunity,
    market_trends = [],
    growth_drivers = [],
    market_challenges = [],
  } = data;

  return (
    <section className="analysis-card">
      <h2>Market Analysis</h2>

      <div className="analysis-block">
        <h3>Industry</h3>
        <p>{industry}</p>
      </div>

      <div className="analysis-block">
        <h3>Market Opportunity</h3>
        <p>{market_opportunity}</p>
      </div>

      {market_trends.length > 0 && (
        <div className="analysis-block">
          <h3>Market Trends</h3>
          <ul>
            {market_trends.map((trend, i) => (
              <li key={i}>{trend}</li>
            ))}
          </ul>
        </div>
      )}

      {growth_drivers.length > 0 && (
        <div className="analysis-block">
          <h3>Growth Drivers</h3>
          <ul>
            {growth_drivers.map((driver, i) => (
              <li key={i}>{driver}</li>
            ))}
          </ul>
        </div>
      )}

      {market_challenges.length > 0 && (
        <div className="analysis-block">
          <h3>Market Challenges</h3>
          <ul>
            {market_challenges.map((challenge, i) => (
              <li key={i}>{challenge}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}