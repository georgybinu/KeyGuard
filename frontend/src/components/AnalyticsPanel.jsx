function formatMetric(value, suffix, digits = 0) {
  if (value == null || Number.isNaN(value)) {
    return `-- ${suffix}`;
  }
  return `${value.toFixed(digits)} ${suffix}`;
}

function AnalyticsPanel({ analytics }) {
  return (
    <section className="dashboard-card analytics-card">
      <div className="card-header-row">
        <div>
          <p className="card-eyebrow">Typing Analytics</p>
          <h3>Live Metrics</h3>
        </div>
      </div>

      <div className="analytics-list">
        <div className="analytics-item">
          <span className="analytics-label">Typing Speed</span>
          <strong>{formatMetric(analytics.wpm, 'WPM')}</strong>
        </div>
        <div className="analytics-item">
          <span className="analytics-label">Average Dwell</span>
          <strong>{formatMetric(analytics.dwellTime, 'ms')}</strong>
        </div>
        <div className="analytics-item">
          <span className="analytics-label">Average Flight</span>
          <strong>{formatMetric(analytics.flightTime, 'ms')}</strong>
        </div>
      </div>

      <p className="card-copy">
        These values refresh from recent windows instead of every single keystroke.
      </p>
    </section>
  );
}

export default AnalyticsPanel;
