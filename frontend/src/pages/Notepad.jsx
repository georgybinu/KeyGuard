import { useEffect, useMemo, useRef, useState } from 'react';
import '../styles/Notepad.css';
import { predictTyping } from '../lib/api';
import ConfidenceMeter from '../components/ConfidenceMeter';
import StatusBanner from '../components/StatusBanner';
import AnalyticsPanel from '../components/AnalyticsPanel';
import {
  consumeKeyUp,
  getAnalysisWindow,
  isIdentitySignalKey,
  isTrackableKey,
  registerKeyDown,
} from '../lib/keystrokes';

const WINDOW_SIZE = 32;
const MIN_SIGNAL_KEYS = 20;
const ANALYSIS_STEP = 10;
const HISTORY_LIMIT = 5;
const ALERT_COOLDOWN_MS = 15000;
const ANALYTICS_REFRESH_MS = 2500;

const SECURITY_STATES = {
  SAFE: 'SAFE',
  SUSPICIOUS: 'SUSPICIOUS',
  INTRUDER: 'INTRUDER',
};

function confidencePercent(value) {
  return `${Math.round((value || 0) * 100)}%`;
}

function computeAnalytics(keystrokes) {
  if (keystrokes.length < 2) {
    return {
      wpm: 0,
      dwellTime: 0,
      flightTime: 0,
    };
  }

  const dwellTimes = keystrokes.map((item) => item.key_release_time - item.key_press_time);
  const flightTimes = keystrokes.slice(1).map((item, index) => {
    const previous = keystrokes[index];
    return Math.max(0, item.key_press_time - previous.key_release_time);
  });

  const durationMs = keystrokes[keystrokes.length - 1].key_release_time - keystrokes[0].key_press_time;
  const wordsTyped = Math.max(keystrokes.length / 5, 0.2);
  const wpm = durationMs > 0 ? wordsTyped / (durationMs / 60000) : 0;

  return {
    wpm,
    dwellTime: dwellTimes.reduce((sum, value) => sum + value, 0) / dwellTimes.length,
    flightTime: flightTimes.length > 0
      ? flightTimes.reduce((sum, value) => sum + value, 0) / flightTimes.length
      : 0,
  };
}

function summarizeHistory(history) {
  return {
    intruderVotes: history.filter((entry) => entry.prediction === 'INTRUDER' && entry.confidence >= 0.75).length,
    suspiciousVotes: history.filter(
      (entry) =>
        entry.prediction === 'SUSPICIOUS' ||
        (entry.prediction === 'INTRUDER' && entry.confidence >= 0.65),
    ).length,
    normalVotes: history.filter((entry) => entry.prediction === 'NORMAL' && entry.confidence >= 0.62).length,
    averageConfidence:
      history.length > 0
        ? history.reduce((sum, entry) => sum + (entry.confidence || 0), 0) / history.length
        : 0,
  };
}

function Notepad({ session }) {
  const [text, setText] = useState('');
  const [keystrokes, setKeystrokes] = useState([]);
  const [monitorState, setMonitorState] = useState(SECURITY_STATES.SAFE);
  const [status, setStatus] = useState('Monitoring will begin after a short typing sample.');
  const [lastResult, setLastResult] = useState(null);
  const [smoothedConfidence, setSmoothedConfidence] = useState(0);
  const [intruderAlert, setIntruderAlert] = useState(null);
  const [recoveryNotice, setRecoveryNotice] = useState('');
  const [analytics, setAnalytics] = useState({
    wpm: 0,
    dwellTime: 0,
    flightTime: 0,
  });

  const pendingKeydownsRef = useRef({});
  const isAnalyzingRef = useRef(false);
  const lastSubmittedCountRef = useRef(0);
  const decisionHistoryRef = useRef([]);
  const lastAlertAtRef = useRef(0);
  const priorStateRef = useRef(SECURITY_STATES.SAFE);

  const stateCopy = useMemo(
    () => ({
      [SECURITY_STATES.SAFE]: 'The last few prediction windows match the genuine user profile.',
      [SECURITY_STATES.SUSPICIOUS]: 'KeyGuard sees unusual rhythm and is waiting for more evidence before escalating.',
      [SECURITY_STATES.INTRUDER]: 'Multiple recent windows look inconsistent with the trained user.',
    }),
    [],
  );

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
    const timerId = window.setInterval(() => {
      const signalWindow = getAnalysisWindow(
        keystrokes.filter((item) => isIdentitySignalKey(item.key)),
        WINDOW_SIZE,
      );

      if (signalWindow.length >= MIN_SIGNAL_KEYS) {
        setAnalytics(computeAnalytics(signalWindow));
      }
    }, ANALYTICS_REFRESH_MS);

    return () => window.clearInterval(timerId);
  }, [keystrokes]);

  useEffect(() => {
    if (keystrokes.length < WINDOW_SIZE) {
      return undefined;
    }

    const timeoutId = window.setTimeout(async () => {
      if (isAnalyzingRef.current || keystrokes.length - lastSubmittedCountRef.current < ANALYSIS_STEP) {
        return;
      }

      const recentWindow = getAnalysisWindow(keystrokes, WINDOW_SIZE);
      const signalWindow = recentWindow.filter((item) => isIdentitySignalKey(item.key));

      if (signalWindow.length < MIN_SIGNAL_KEYS) {
        setStatus('Waiting for more letter and symbol activity before the next identity check.');
        return;
      }

      isAnalyzingRef.current = true;

      try {
        const result = await predictTyping({
          username: session.username,
          session_token: session.session_token,
          keystrokes: signalWindow,
        });

        lastSubmittedCountRef.current = keystrokes.length;
        setLastResult(result);

        const nextHistory = [
          ...decisionHistoryRef.current,
          { prediction: result.prediction, confidence: result.confidence, at: Date.now() },
        ].slice(-HISTORY_LIMIT);
        decisionHistoryRef.current = nextHistory;

        const historySummary = summarizeHistory(nextHistory);
        setSmoothedConfidence(historySummary.averageConfidence || result.confidence || 0);

        let nextState = SECURITY_STATES.SAFE;

        if (historySummary.intruderVotes >= 2 && historySummary.suspiciousVotes >= 3) {
          nextState = SECURITY_STATES.INTRUDER;
        } else if (
          historySummary.suspiciousVotes >= 2 ||
          result.prediction === 'SUSPICIOUS' ||
          (result.prediction === 'INTRUDER' && result.confidence < 0.75)
        ) {
          nextState = SECURITY_STATES.SUSPICIOUS;
        }

        const previousState = priorStateRef.current;
        priorStateRef.current = nextState;
        setMonitorState(nextState);
        setStatus(stateCopy[nextState]);

        if (nextState === SECURITY_STATES.INTRUDER) {
          const now = Date.now();
          setRecoveryNotice('');
          if (now - lastAlertAtRef.current >= ALERT_COOLDOWN_MS) {
            setIntruderAlert(result);
            lastAlertAtRef.current = now;
          }
        } else if (previousState === SECURITY_STATES.INTRUDER && nextState === SECURITY_STATES.SAFE) {
          setRecoveryNotice(`Genuine user detected again (${confidencePercent(historySummary.averageConfidence)})`);
          setIntruderAlert(null);
        } else if (nextState !== SECURITY_STATES.INTRUDER) {
          setIntruderAlert(null);
          if (nextState === SECURITY_STATES.SUSPICIOUS) {
            setRecoveryNotice('');
          }
        }
      } catch (error) {
        setStatus(error.message || 'Live monitoring is temporarily unavailable.');
      } finally {
        isAnalyzingRef.current = false;
      }
    }, 700);

    return () => window.clearTimeout(timeoutId);
  }, [keystrokes, session.session_token, session.username, stateCopy]);

  return (
    <section className="notepad-shell">
      <div className="notepad-header">
        <div>
          <p className="panel-eyebrow">Protected Workspace</p>
          <h2>Authentication Dashboard</h2>
          <p className="panel-copy">
            Type naturally while KeyGuard analyzes recent windows in the background and updates the dashboard with smoothed security feedback.
          </p>
        </div>
        <div className="notepad-stats">
          <div className="mini-stat">
            <span className="mini-label">User</span>
            <strong>{session.username}</strong>
          </div>
          <div className="mini-stat">
            <span className="mini-label">Monitoring</span>
            <strong>{monitorState}</strong>
          </div>
          <div className="mini-stat">
            <span className="mini-label">Latest Result</span>
            <strong>{lastResult?.prediction || 'Pending'}</strong>
          </div>
        </div>
      </div>

      <StatusBanner state={monitorState} statusText={status} />

      {recoveryNotice && (
        <div className="recovery-banner">
          <span className="recovery-icon">✓</span>
          <span>{recoveryNotice}</span>
        </div>
      )}

      <div className="dashboard-layout">
        <div className="typing-panel">
          <div className="typing-panel-header">
            <div>
              <p className="card-eyebrow">Secure Typing Area</p>
              <h3>Monitored Notepad</h3>
            </div>
            <div className="typing-panel-meta">
              <span>Signal Keys: {keystrokes.filter((item) => isIdentitySignalKey(item.key)).length}</span>
            </div>
          </div>

          <textarea
            className="notepad-input"
            value={text}
            onChange={(event) => setText(event.target.value)}
            onKeyDown={handleKeyDown}
            onKeyUp={handleKeyUp}
            placeholder="Start typing here. KeyGuard will keep checking your typing rhythm in the background..."
          />
        </div>

        <aside className="dashboard-sidebar">
          <ConfidenceMeter confidence={smoothedConfidence || lastResult?.confidence || 0} />
          <AnalyticsPanel analytics={analytics} />

          <section className="dashboard-card details-card">
            <div className="card-header-row">
              <div>
                <p className="card-eyebrow">Monitoring Logic</p>
                <h3>How It Works</h3>
              </div>
            </div>
            <p className="card-copy">
              Predictions are made from sliding windows of recent keystrokes. The interface shows smoothed confidence and status changes only after repeated evidence.
            </p>
          </section>
        </aside>
      </div>

      {intruderAlert && (
        <div className="intruder-modal-backdrop" role="presentation">
          <div className="intruder-modal" role="alertdialog" aria-labelledby="intruder-title" aria-modal="true">
            <p className="intruder-kicker">Security Alert</p>
            <h3 id="intruder-title">Intruder detected</h3>
            <p>
              Multiple recent typing windows deviate significantly from {session.username}&apos;s trained profile.
            </p>
            <p className="intruder-confidence">
              Confidence: {confidencePercent(intruderAlert.confidence)}
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
