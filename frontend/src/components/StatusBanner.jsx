const STATUS_META = {
  SAFE: {
    title: 'System Secure',
    detail: 'Recent windows match the trained typing profile.',
    tone: 'safe',
  },
  SUSPICIOUS: {
    title: 'Suspicious Activity',
    detail: 'The system sees unusual rhythm and is collecting more evidence.',
    tone: 'suspicious',
  },
  INTRUDER: {
    title: 'Intruder Detected',
    detail: 'Multiple recent windows deviate significantly from the trained profile.',
    tone: 'intruder',
  },
};

function StatusBanner({ state, statusText }) {
  const meta = STATUS_META[state] || STATUS_META.SAFE;

  return (
    <section className={`status-banner ${meta.tone}`}>
      <span className={`status-indicator ${meta.tone}`} aria-hidden="true" />
      <div>
        <p className="status-title">{meta.title}</p>
        <p className="status-detail">{statusText || meta.detail}</p>
      </div>
    </section>
  );
}

export default StatusBanner;
