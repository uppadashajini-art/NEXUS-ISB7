export default function MarketGaps({ gaps }) {
  if (!gaps || gaps.length === 0) return null;

  return (
    <section className="analysis-card">
      <h2>Market Gaps</h2>
      <ul>
        {gaps.map((gap, i) => (
          <li key={i}>{gap}</li>
        ))}
      </ul>
    </section>
  );
}