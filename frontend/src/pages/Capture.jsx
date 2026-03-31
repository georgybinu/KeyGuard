import { useEffect, useMemo, useRef, useState } from 'react';
import '../styles/Capture.css';
import { submitTrainingRound } from '../lib/api';
import { consumeKeyUp, isTrackableKey, registerKeyDown } from '../lib/keystrokes';

function Capture({ user, onComplete }) {
  const phraseBank = useMemo(
    () => [
      'secure identities begin with steady typing',
      'behavioral biometrics protect sensitive notes',
      'typing rhythm reveals who is at the keyboard',
      'an attentive system can spot unusual behavior',
      'fastapi services power this authentication demo',
      'continuous verification keeps sessions safer',
      'well trained profiles improve anomaly detection',
      'every phrase helps shape a stronger baseline',
      'users should feel protected without friction',
      'keystroke timing becomes a digital signature',
      'careful models can separate owners from intruders',
      'trusted sessions deserve silent background checks',
      'security works best when it respects the user',
      'precision in timing creates a unique pattern',
      'note taking stays open while identity is checked',
    ],
    [],
  );

  const [phase, setPhase] = useState('ready');
  const [currentRound, setCurrentRound] = useState(0);
  const [typedText, setTypedText] = useState('');
  const [keystrokes, setKeystrokes] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [trainingPhrases, setTrainingPhrases] = useState([]);
  const [lastSummary, setLastSummary] = useState(null);
  const inputRef = useRef(null);
  const pendingKeyDownsRef = useRef({});

  const REQUIRED_ROUNDS = 10;

  useEffect(() => {
    const shuffled = [...phraseBank].sort(() => Math.random() - 0.5);
    setTrainingPhrases(shuffled.slice(0, REQUIRED_ROUNDS));
  }, [phraseBank]);

  useEffect(() => {
    if (phase === 'training') {
      inputRef.current?.focus();
    }
  }, []);

  const currentPhrase = trainingPhrases[currentRound] || '';

  const handleKeyDown = (e) => {
    if (phase !== 'training' || !isTrackableKey(e.key)) {
      return;
    }
    pendingKeyDownsRef.current = registerKeyDown(pendingKeyDownsRef.current, e.key, Date.now());
  };

  const handleKeyUp = (e) => {
    if (phase !== 'training' || !isTrackableKey(e.key)) {
      return;
    }
    const result = consumeKeyUp(pendingKeyDownsRef.current, e.key, Date.now());
    pendingKeyDownsRef.current = result.pendingKeydowns;
    if (result.keystroke) {
      setKeystrokes((prev) => [...prev, result.keystroke]);
    }
  };

  const handleInput = (e) => {
    setTypedText(e.target.value);
  };

  const startTraining = () => {
    setPhase('training');
    setCurrentRound(0);
    setTypedText('');
    setKeystrokes([]);
    pendingKeyDownsRef.current = {};
    setLastSummary(null);
    setMessage('');
  };

  const submitRound = async () => {
    if (typedText.trim() !== currentPhrase.trim()) {
      setMessage('❌ Text must match exactly. Try again.');
      return;
    }

    setLoading(true);
    try {
      const response = await submitTrainingRound({
        username: user.username,
        keystrokes,
        round: currentRound + 1,
        phrase: currentPhrase,
      });
      setLastSummary(response.profile_summary);
      const nextRound = currentRound + 1;

      if (nextRound === REQUIRED_ROUNDS) {
        setPhase('completed');
        setMessage('Training complete. Redirecting to your protected notepad.');
        setTimeout(() => {
          onComplete?.({
            trainingRounds: response.profile_summary.trained_rounds,
            trainingCompleted: response.profile_summary.training_completed,
          });
        }, 900);
      } else {
        setCurrentRound(nextRound);
        setTypedText('');
        setKeystrokes([]);
        pendingKeyDownsRef.current = {};
        setMessage('');
      }
    } catch (err) {
      setMessage(err.message || 'Unable to save the training round.');
    }
    setLoading(false);
  };

  const progress = ((phase === 'completed' ? REQUIRED_ROUNDS : currentRound) / REQUIRED_ROUNDS) * 100;
  const isTextMatched = typedText.trim() === currentPhrase.trim();

  return (
    <div className="capture-container">
      <div className="capture-card">
        {phase === 'ready' && (
          <div className="phase-ready">
            <h2>Build Your Typing Profile</h2>
            <p>Type 10 short phrases so KeyGuard can learn how you naturally use the keyboard.</p>
            
            <div className="training-info">
              <div className="info-row">
                <span className="label">User</span>
                <span className="value">{user.username}</span>
              </div>
              <div className="info-row">
                <span className="label">Rounds</span>
                <span className="value">{REQUIRED_ROUNDS}</span>
              </div>
              <div className="info-row">
                <span className="label">Signals</span>
                <span className="value">Press, release, dwell, flight</span>
              </div>
              <div className="info-row">
                <span className="label">Afterward</span>
                <span className="value">Protected notepad access</span>
              </div>
            </div>

            <button className="btn btn-primary" onClick={startTraining}>
              Start Training
            </button>
          </div>
        )}

        {phase === 'training' && (
          <div className="phase-training">
            <div className="training-header">
              <div className="round-indicator">
                Round <strong>{currentRound + 1}</strong> of {REQUIRED_ROUNDS}
              </div>
              <div className="progress-wrapper">
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                </div>
                <div className="progress-text">{Math.round(progress)}%</div>
              </div>
            </div>

            <div className="phrase-box">
              <p className="phrase-label">Type this phrase:</p>
              <p className="phrase-text">{currentPhrase}</p>
            </div>

            <textarea
              ref={inputRef}
              className="input-field"
              placeholder="Click here and start typing..."
              value={typedText}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              onKeyUp={handleKeyUp}
            />

            <div className={`match-status ${isTextMatched ? 'matched' : ''}`}>
              {isTextMatched ? (
                <>
                  <span className="icon">✓</span>
                  <span>Phrase matched!</span>
                </>
              ) : (
                <>
                  <span className="icon">○</span>
                  <span>{typedText.length}/{currentPhrase.length} characters</span>
                </>
              )}
            </div>

            <button
              className="btn btn-primary"
              onClick={submitRound}
              disabled={!isTextMatched || loading}
            >
              {loading ? 'Submitting...' : 'Continue'}
            </button>

            {message && <div className="message">{message}</div>}
          </div>
        )}

        {phase === 'completed' && (
          <div className="phase-completed">
            <div className="completion-icon">✓</div>
            <h2>Profile Ready</h2>
            <p>Your typing baseline has been stored. Opening the monitored notepad now.</p>

            <div className="completion-stats">
              <div className="stat">
                <span className="stat-label">Rounds Completed</span>
                <span className="stat-value">{REQUIRED_ROUNDS}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Profile Features</span>
                <span className="stat-value">{lastSummary?.features_available?.length || 5}</span>
              </div>
            </div>

            <p className="next-step">{message}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Capture;
