export default function CustomerSegments({ segments }) {
  if (!segments || segments.length === 0) return null;

  return (
    <section className="analysis-card">
      <h2>Customer Segments</h2>

      {segments.map((seg, i) => (
        <div className="segment-block" key={i}>
          <h3>{seg.segment}</h3>

          {seg.needs && seg.needs.length > 0 && (
            <>
              <h4>Needs</h4>
              <ul>
                {seg.needs.map((need, j) => (
                  <li key={j}>{need}</li>
                ))}
              </ul>
            </>
          )}

          {seg.pain_points && seg.pain_points.length > 0 && (
            <>
              <h4>Pain Points</h4>
              <ul>
                {seg.pain_points.map((point, j) => (
                  <li key={j}>{point}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      ))}
    </section>
  );
}