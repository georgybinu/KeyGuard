import React, { useState, useRef, useEffect } from 'react';
import '../styles/Capture.css';

function Capture({ user, onComplete }) {
  // Training phrases - we'll randomize and show one per round
  const TRAINING_PHRASES = [
    'the quick brown fox jumps',
    'keystroke patterns are unique',
    'secure authentication system',
    'typing dynamics analysis',
    'biometric security measures',
    'machine learning models',
    'intrusion detection system',
    'behavioral authentication',
    'digital identity verification',
    'continuous user monitoring'
  ];

  const [phase, setPhase] = useState('ready');
  const [currentRound, setCurrentRound] = useState(0);
  const [currentPhrase, setCurrentPhrase] = useState('');
  const [typedText, setTypedText] = useState('');
  const [keystrokes, setKeystrokes] = useState([]);
  const [allKeystrokes, setAllKeystrokes] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [phrasesList, setPhrasesList] = useState([]);
  const inputRef = useRef(null);

  const REQUIRED_ROUNDS = 10;

  // Initialize phrases list on mount
  useEffect(() => {
    const shuffled = [...TRAINING_PHRASES].sort(() => Math.random() - 0.5);
    setPhrasesList(shuffled);
  }, []);

  // Set current phrase when round changes
  useEffect(() => {
    if (phrasesList.length > 0 && phase === 'training') {
      setCurrentPhrase(phrasesList[currentRound]);
    }
  }, [currentRound, phase, phrasesList]);

  const handleKeyDown = (e) => {
    if (phase !== 'training') return;
    
    const keystroke = {
      key: e.key,
      timestamp: Date.now(),
      type: 'keydown'
    };
    setKeystrokes(prev => [...prev, keystroke]);
  };

  const handleKeyUp = (e) => {
    if (phase !== 'training') return;
    
    const keystroke = {
      key: e.key,
      timestamp: Date.now(),
      type: 'keyup'
    };
    setKeystrokes(prev => [...prev, keystroke]);
  };

  const handleInput = (e) => {
    setTypedText(e.target.value);
  };

  const startTraining = () => {
    setPhase('training');
    setCurrentRound(0);
    setTypedText('');
    setKeystrokes([]);
    setMessage('');
    inputRef.current?.focus();
  };

  const submitRound = async () => {
    if (typedText.trim() !== currentPhrase.trim()) {
      setMessage('❌ Text must match exactly. Try again.');
      return;
    }

    setLoading(true);
    try {
      // Submit to backend
      const response = await fetch('http://localhost:8000/train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: user.username,
          keystrokes: keystrokes,
          round: currentRound + 1
        })
      });

      if (response.ok) {
        setAllKeystrokes(prev => [...prev, ...keystrokes]);
        const nextRound = currentRound + 1;

        if (nextRound === REQUIRED_ROUNDS) {
          // Training complete
          setPhase('completed');
          setMessage('✅ Training complete! Your profile is ready.');
          
          setTimeout(() => {
            if (onComplete) {
              onComplete({
                rounds: REQUIRED_ROUNDS,
                totalKeystrokes: allKeystrokes.length + keystrokes.length,
                features: { trained: true }
              });
            }
          }, 1500);
        } else {
          // Next round
          setCurrentRound(nextRound);
          setTypedText('');
          setKeystrokes([]);
          setMessage('');
          inputRef.current?.focus();
        }
      } else {
        setMessage('❌ Error submitting training data.');
      }
    } catch (err) {
      setMessage('❌ Connection error. Make sure backend is running.');
    }
    setLoading(false);
  };

  const progress = (currentRound / REQUIRED_ROUNDS) * 100;
  const isTextMatched = typedText.trim() === currentPhrase.trim();

  return (
    <div className="capture-container">
      <div className="capture-card">
        {phase === 'ready' && (
          <div className="phase-ready">
            <h2>Train Your Profile</h2>
            <p>Create your unique keystroke fingerprint</p>
            
            <div className="training-info">
              <div className="info-row">
                <span className="label">Rounds</span>
                <span className="value">{REQUIRED_ROUNDS}</span>
              </div>
              <div className="info-row">
                <span className="label">Time</span>
                <span className="value">~3 mins</span>
              </div>
              <div className="info-row">
                <span className="label">Measures</span>
                <span className="value">Dwell & Flight time</span>
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
            <h2>Training Complete</h2>
            <p>Your keystroke profile is now ready for authentication</p>

            <div className="completion-stats">
              <div className="stat">
                <span className="stat-label">Rounds Completed</span>
                <span className="stat-value">{REQUIRED_ROUNDS}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Keystrokes Recorded</span>
                <span className="stat-value">{allKeystrokes.length + keystrokes.length}</span>
              </div>
            </div>

            <p className="next-step">Ready to test your authentication</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Capture;
