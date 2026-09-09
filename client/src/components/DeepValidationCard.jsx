
function DeepValidationCard({ technical, scientific, regulatory }) {
  const getScore = (data) => {
    if (!data) return null;

    if (typeof data === "number") {
      return data;
    }

    if (typeof data?.score === "number") {
      return data.score;
    }

    if (typeof data?.confidence === "number") {
      return data.confidence;
    }

    return null;
  };

  const formatValue = (value) => {
    if (value === null || value === undefined || value === "") {
      return "No data available";
    }

    if (typeof value === "string" || typeof value === "number") {
      return String(value);
    }

    return null;
  };

  const renderSection = (title, icon, data) => {
    const score = getScore(data);

    return (
      <div className="deep-validation-item">
        <div className="deep-validation-header">
          <div className="deep-validation-title">
            <span className="deep-validation-icon">{icon}</span>
            <h4>{title}</h4>
          </div>

          {score !== null && (
            <span className="deep-validation-score">
              {score <= 1 ? `${Math.round(score * 100)}%` : `${Math.round(score)}%`}
            </span>
          )}
        </div>

        <div className="deep-validation-content">
          {formatValue(data) ? (
            <p>{formatValue(data)}</p>
          ) : data ? (
            <>
              {data.summary && <p>{data.summary}</p>}

              {data.assessment && (
                <p>
                  <strong>Assessment:</strong> {data.assessment}
                </p>
              )}

              {data.status && (
                <p>
                  <strong>Status:</strong> {data.status}
                </p>
              )}

              {data.reasoning && (
                <p>
                  <strong>Reasoning:</strong> {data.reasoning}
                </p>
              )}

              {data.risks && Array.isArray(data.risks) && (
                <div className="deep-validation-list">
                  <strong>Risks:</strong>
                  <ul>
                    {data.risks.map((risk, index) => (
                      <li key={index}>{String(risk)}</li>
                    ))}
                  </ul>
                </div>
              )}

              {data.recommendations &&
                Array.isArray(data.recommendations) && (
                  <div className="deep-validation-list">
                    <strong>Recommendations:</strong>
                    <ul>
                      {data.recommendations.map((recommendation, index) => (
                        <li key={index}>{String(recommendation)}</li>
                      ))}
                    </ul>
                  </div>
                )}

              {!data.summary &&
                !data.assessment &&
                !data.status &&
                !data.reasoning &&
                !data.risks &&
                !data.recommendations && (
                  <pre className="deep-validation-json">
                    {JSON.stringify(data, null, 2)}
                  </pre>
                )}
            </>
          ) : (
            <p>No data available</p>
          )}
        </div>
      </div>
    );
  };

  return (
    <section className="deep-validation-card">
      <div className="deep-validation-card-header">
        <div>
          <span className="section-label">DEEP VALIDATION</span>
          <h2>Advanced Validation Matrix</h2>
          <p>
            AI-powered validation across technical, scientific, and
            regulatory dimensions.
          </p>
        </div>
      </div>

      <div className="deep-validation-grid">
        {renderSection("Technical Feasibility", "⚙️", technical)}
        {renderSection("Scientific Validation", "🔬", scientific)}
        {renderSection("Regulatory Risk", "⚖️", regulatory)}
      </div>
    </section>
  );
}

export default DeepValidationCard;

