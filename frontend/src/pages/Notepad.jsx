import { useEffect, useRef, useState } from 'react';
import '../styles/Notepad.css';
import { predictTyping } from '../lib/api';
import { consumeKeyUp, getAnalysisWindow, isTrackableKey, registerKeyDown } from '../lib/keystrokes';

const MIN_ANALYSIS_KEYS = 24;
const MIN_NON_SPACE_KEYS = 12;
const ANALYSIS_STEP = 8;
const HISTORY_LIMIT = 5;
const ALERT_COOLDOWN_MS = 15000;

function Notepad({ session }) {
  const [text, setText] = useState('');
  const [keystrokes, setKeystrokes] = useState([]);
  const [status, setStatus] = useState('Monitoring will begin after a short typing sample.');
  const [lastResult, setLastResult] = useState(null);
  const [intruderAlert, setIntruderAlert] = useState(null);
  const [recoveryNotice, setRecoveryNotice] = useState('');
  const pendingKeydownsRef = useRef({});
  const isAnalyzingRef = useRef(false);
  const lastSubmittedCountRef = useRef(0);
  const decisionHistoryRef = useRef([]);
  const lastAlertAtRef = useRef(0);
  const wasIntruderStateRef = useRef(false);

  const handleKeyDown = (event) => {
    if (!isTrackableKey(event.key)) {
      return;
    }
    pendingKeydownsRef.current = registerKeyDown(pendingKeydownsRef.current, event.key, Date.now());
  };

  const handleKeyUp = (event) => {
    if (!isTrackableKey(event.key)) {
      return;
    }

    const result = consumeKeyUp(pendingKeydownsRef.current, event.key, Date.now());
    pendingKeydownsRef.current = result.pendingKeydowns;
    if (result.keystroke) {
      setKeystrokes((previous) => [...previous, result.keystroke]);
    }
  };

  useEffect(() => {
    if (keystrokes.length < MIN_ANALYSIS_KEYS) {
      return undefined;
    }

    const timeoutId = window.setTimeout(async () => {
      if (
        isAnalyzingRef.current ||
        keystrokes.length - lastSubmittedCountRef.current < ANALYSIS_STEP
      ) {
        return;
      }

      isAnalyzingRef.current = true;
      const windowedKeystrokes = getAnalysisWindow(keystrokes, MIN_ANALYSIS_KEYS);
      const nonSpaceCount = windowedKeystrokes.filter((item) => item.key !== ' ').length;

      if (nonSpaceCount < MIN_NON_SPACE_KEYS) {
        setStatus('Waiting for more non-space typing before the next identity check.');
        isAnalyzingRef.current = false;
        return;
      }

      try {
        setStatus('Analyzing your recent typing rhythm...');
        const result = await predictTyping({
          username: session.username,
          session_token: session.session_token,
          keystrokes: windowedKeystrokes,
        });
        lastSubmittedCountRef.current = keystrokes.length;
        setLastResult(result);
        setRecoveryNotice('');

        const nextHistory = [
          ...decisionHistoryRef.current,
          { prediction: result.prediction, confidence: result.confidence, at: Date.now() },
        ].slice(-HISTORY_LIMIT);
        decisionHistoryRef.current = nextHistory;

        const intruderVotes = nextHistory.filter(
          (entry) => entry.prediction === 'INTRUDER' && entry.confidence >= 0.72,
        ).length;
        const suspiciousVotes = nextHistory.filter(
          (entry) => entry.prediction === 'INTRUDER' || entry.prediction === 'SUSPICIOUS',
        ).length;
        const normalVotes = nextHistory.filter(
          (entry) => entry.prediction === 'NORMAL' && entry.confidence >= 0.65,
        ).length;
        const now = Date.now();

        if (intruderVotes >= 2 && suspiciousVotes >= 3) {
          setStatus('Potential intruder detected.');
          if (now - lastAlertAtRef.current >= ALERT_COOLDOWN_MS) {
            setIntruderAlert(result);
            lastAlertAtRef.current = now;
          }
          wasIntruderStateRef.current = true;
        } else if (result.prediction === 'SUSPICIOUS') {
          setStatus('Typing looks unusual, but KeyGuard is waiting for more evidence.');
        } else {
          setStatus('Typing pattern matches the trained user.');
          if (wasIntruderStateRef.current && normalVotes >= 3) {
            setRecoveryNotice('Genuine user detected');
            wasIntruderStateRef.current = false;
          }
        }
      } catch (error) {
        setStatus(error.message || 'Live monitoring is temporarily unavailable.');
      } finally {
        isAnalyzingRef.current = false;
      }
    }, 700);

    return () => window.clearTimeout(timeoutId);
  }, [keystrokes, session.session_token, session.username]);

  return (
    <section className="notepad-shell">
      <div className="notepad-header">
        <div>
          <p className="panel-eyebrow">Protected Workspace</p>
          <h2>Monitored Notepad</h2>
          <p className="panel-copy">
            Type naturally. KeyGuard continuously compares your live rhythm with your trained profile.
          </p>
        </div>
        <div className="notepad-stats">
          <div className="mini-stat">
            <span className="mini-label">User</span>
            <strong>{session.username}</strong>
          </div>
          <div className="mini-stat">
            <span className="mini-label">Captured Keys</span>
            <strong>{keystrokes.length}</strong>
          </div>
          <div className="mini-stat">
            <span className="mini-label">Last Result</span>
            <strong>{lastResult?.prediction || 'Pending'}</strong>
          </div>
        </div>
      </div>

      <div className="status-strip">
        <span className={`status-dot ${lastResult?.prediction === 'INTRUDER' ? 'danger' : lastResult?.prediction === 'SUSPICIOUS' ? 'warn' : 'safe'}`} />
        <span>{status}</span>
      </div>

      {recoveryNotice && (
        <div className="recovery-banner">
          <span className="recovery-icon">✓</span>
          <span>{recoveryNotice}</span>
        </div>
      )}

      <textarea
        className="notepad-input"
        value={text}
        onChange={(event) => setText(event.target.value)}
        onKeyDown={handleKeyDown}
        onKeyUp={handleKeyUp}
        placeholder="Start typing here. Your keystroke dynamics will be checked in the background..."
      />

      <div className="analysis-grid">
        <div className="analysis-card">
          <h3>Live Monitoring</h3>
          <p>Key press time, key release time, dwell time, and flight time are captured as you type.</p>
        </div>
        <div className="analysis-card">
          <h3>Decision Engine</h3>
          <p>KeyGuard uses a user-specific One-Class SVM and your saved baseline profile for anomaly detection.</p>
        </div>
        <div className="analysis-card">
          <h3>Confidence</h3>
          <p>{lastResult ? `${Math.round(lastResult.confidence * 100)}% confidence in the latest decision.` : 'Confidence will appear after the first analysis window.'}</p>
        </div>
      </div>

      {intruderAlert && (
        <div className="intruder-modal-backdrop" role="presentation">
          <div className="intruder-modal" role="alertdialog" aria-labelledby="intruder-title" aria-modal="true">
            <p className="intruder-kicker">Security Alert</p>
            <h3 id="intruder-title">Intruder detected</h3>
            <p>
              The latest typing sample deviates significantly from {session.username}&apos;s trained profile.
            </p>
            <p className="intruder-confidence">
              Confidence: {Math.round(intruderAlert.confidence * 100)}%
            </p>
            <button className="dismiss-alert" onClick={() => setIntruderAlert(null)}>
              Dismiss
            </button>
          </div>
        </div>
      )}
    </section>
  );
}

export default Notepad;
