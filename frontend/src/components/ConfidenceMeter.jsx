function getConfidenceTone(confidence) {
  if (confidence > 0.85) {
    return {
      tone: 'genuine',
      label: 'Genuine',
    };
  }

  if (confidence >= 0.6) {
    return {
      tone: 'suspicious',
      label: 'Suspicious',
    };
  }

  return {
    tone: 'intruder',
    label: 'Intruder',
  };
}

function ConfidenceMeter({ confidence = 0 }) {
  const percentage = Math.round(confidence * 100);
  const tone = getConfidenceTone(confidence);

  return (
    <section className="dashboard-card confidence-card">
      <div className="card-header-row">
        <div>
          <p className="card-eyebrow">Model Confidence</p>
          <h3>Confidence Meter</h3>
        </div>
        <span className={`tone-pill ${tone.tone}`}>{tone.label}</span>
      </div>

      <div className="confidence-value">Confidence: {percentage}%</div>
      <div className="confidence-track" aria-hidden="true">
        <div
          className={`confidence-fill ${tone.tone}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <p className="card-copy">
        Confidence is smoothed across recent prediction windows to avoid sudden swings.
      </p>
    </section>
  );
}

export default ConfidenceMeter;
