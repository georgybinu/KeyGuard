import { useEffect, useMemo, useRef, useState } from 'react';
import '../styles/Capture.css';
import { submitTrainingRound } from '../lib/api';
import { consumeKeyUp, isTrackableKey, registerKeyDown } from '../lib/keystrokes';

const PHRASE_ROUNDS = 10;
const PARAGRAPH_ROUNDS = 3;
const TOTAL_ROUNDS = PHRASE_ROUNDS + PARAGRAPH_ROUNDS;

const PARAGRAPHS = [
  'On quiet mornings I open my notes, plan the day, and reply to a few messages before class begins. The short routine feels normal, calm, and easy to type without rushing.',
  'A light breeze moved through the garden while bright birds crossed the sky above the trees. Small details like weather, motion, and pause patterns help create natural typing rhythm.',
  'After lunch I read a chapter, fixed a tiny bug, and wrote down fresh ideas for tomorrow. Simple daily tasks usually produce the most honest and consistent typing behavior.',
];

function normalizeText(value) {
  return value.replace(/\s+/g, ' ').trim();
}

function computePromptMetrics(keystrokes) {
  if (keystrokes.length === 0) {
    return {
      pressTime: 0,
      releaseTime: 0,
      dwellTime: 0,
      flightTime: 0,
    };
  }

  const dwellTimes = keystrokes.map((item) => item.key_release_time - item.key_press_time);
  const flightTimes = keystrokes.slice(1).map((item, index) => (
    Math.max(0, item.key_press_time - keystrokes[index].key_release_time)
  ));

  const dwellAverage = dwellTimes.reduce((sum, value) => sum + value, 0) / dwellTimes.length;
  const flightAverage = flightTimes.length > 0
    ? flightTimes.reduce((sum, value) => sum + value, 0) / flightTimes.length
    : 0;

  return {
    pressTime: keystrokes.length > 0 ? keystrokes[0].key_press_time : 0,
    releaseTime: keystrokes.length > 0 ? keystrokes[keystrokes.length - 1].key_release_time : 0,
    dwellTime: dwellAverage,
    flightTime: flightAverage,
  };
}

function buildPrompts(phraseBank) {
  const shuffled = [...phraseBank].sort(() => Math.random() - 0.5);
  const phrasePrompts = shuffled.slice(0, PHRASE_ROUNDS).map((text, index) => ({
    id: `phrase-${index + 1}`,
    type: 'phrase',
    promptText: text,
    label: `Phrase ${index + 1}`,
  }));
  const paragraphPrompts = PARAGRAPHS.map((text, index) => ({
    id: `paragraph-${index + 1}`,
    type: 'paragraph',
    promptText: text,
    label: `Paragraph ${index + 1}`,
  }));
  return [...phrasePrompts, ...paragraphPrompts];
}

function Capture({ user, onComplete }) {
  const phraseBank = useMemo(
    () => [
      'Bright morning sunlight filled the quiet room.',
      'My favorite jacket was packed for the trip.',
      'We solved the puzzle after several quick tries.',
      'Fresh coffee makes early study sessions easier.',
      'A small zebra wandered near the dusty road.',
      'The music faded just before the final scene.',
      'Every student writes notes in a different way.',
      'Warm soup and bread were served at noon.',
      'Curious minds explore books, maps, and ideas.',
      'The project update was ready by Friday noon.',
      'Heavy rain mixed with wind and distant thunder.',
      'A clever fox jumped over the broken fence.',
      'Travel plans changed when the airport grew busy.',
      'Quiet waves washed over the bright sandy shore.',
      'Learning new skills takes patience and practice.',
      'The bakery sold warm pies, jam, and soft rolls.',
      'Smart devices connect homes, schools, and offices.',
      'A young artist sketched shapes with bold lines.',
    ],
    [],
  );

  const [phase, setPhase] = useState('ready');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [typedText, setTypedText] = useState('');
  const [keystrokes, setKeystrokes] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [trainingPrompts, setTrainingPrompts] = useState([]);
  const [lastSummary, setLastSummary] = useState(null);
  const inputRef = useRef(null);
  const pendingKeyDownsRef = useRef({});

  useEffect(() => {
    setTrainingPrompts(buildPrompts(phraseBank));
  }, [phraseBank]);

  useEffect(() => {
    if (phase === 'training') {
      inputRef.current?.focus();
    }
  }, [phase, currentIndex]);

  const currentPrompt = trainingPrompts[currentIndex] || null;
  const promptText = currentPrompt?.promptText || '';
  const normalizedTypedText = normalizeText(typedText);
  const normalizedPromptText = normalizeText(promptText);
  const isTextMatched = normalizedTypedText === normalizedPromptText;
  const promptMetrics = computePromptMetrics(keystrokes);

  const handleKeyDown = (event) => {
    if (phase !== 'training' || !isTrackableKey(event.key)) {
      return;
    }
    pendingKeyDownsRef.current = registerKeyDown(pendingKeyDownsRef.current, event.key, Date.now());
  };

  const handleKeyUp = (event) => {
    if (phase !== 'training' || !isTrackableKey(event.key)) {
      return;
    }
    const result = consumeKeyUp(pendingKeyDownsRef.current, event.key, Date.now());
    pendingKeyDownsRef.current = result.pendingKeydowns;
    if (result.keystroke) {
      setKeystrokes((prev) => [...prev, result.keystroke]);
    }
  };

  const resetCurrentPrompt = () => {
    setTypedText('');
    setKeystrokes([]);
    pendingKeyDownsRef.current = {};
  };

  const startTraining = () => {
    setTrainingPrompts(buildPrompts(phraseBank));
    setPhase('training');
    setCurrentIndex(0);
    setLastSummary(null);
    setMessage('');
    resetCurrentPrompt();
  };

  const submitRound = async () => {
    if (!currentPrompt) {
      return;
    }

    if (!isTextMatched) {
      setMessage('Text must match the prompt before continuing.');
      return;
    }

    setLoading(true);
    try {
      const response = await submitTrainingRound({
        username: user.username,
        keystrokes,
        round: currentIndex + 1,
        phrase: currentPrompt.type === 'phrase' ? promptText : null,
        sample_type: currentPrompt.type,
        prompt_text: promptText,
        typed_text: typedText,
      });
      setLastSummary(response.profile_summary);
      const nextIndex = currentIndex + 1;

      if (nextIndex === TOTAL_ROUNDS) {
        setPhase('completed');
        setMessage('Training complete. Redirecting to your protected notepad.');
        window.setTimeout(() => {
          onComplete?.({
            trainingRounds: response.profile_summary.trained_rounds,
            trainingCompleted: response.profile_summary.training_completed,
          });
        }, 900);
      } else {
        setCurrentIndex(nextIndex);
        resetCurrentPrompt();
        setMessage('');
      }
    } catch (error) {
      setMessage(error.message || 'Unable to save the training sample.');
    }
    setLoading(false);
  };

  const progress = ((phase === 'completed' ? TOTAL_ROUNDS : currentIndex) / TOTAL_ROUNDS) * 100;
  const currentStage = currentPrompt?.type === 'paragraph' ? 'Natural Paragraphs' : 'Fixed Phrases';

  return (
    <div className="capture-container">
      <div className="capture-card capture-card-wide">
        {phase === 'ready' && (
          <div className="phase-ready">
            <h2>Build Your Typing Profile</h2>
            <p>KeyGuard trains in two stages: short phrases for controlled timing and short paragraphs for more natural typing rhythm.</p>

            <div className="training-info">
              <div className="info-row">
                <span className="label">User</span>
                <span className="value">{user.username}</span>
              </div>
              <div className="info-row">
                <span className="label">Phase 1</span>
                <span className="value">{PHRASE_ROUNDS} fixed phrases</span>
              </div>
              <div className="info-row">
                <span className="label">Phase 2</span>
                <span className="value">{PARAGRAPH_ROUNDS} natural paragraphs</span>
              </div>
              <div className="info-row">
                <span className="label">Signals</span>
                <span className="value">Press, release, dwell, flight, pace</span>
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

        {phase === 'training' && currentPrompt && (
          <div className="phase-training">
            <div className="training-topbar">
              <div>
                <span className={`phase-badge ${currentPrompt.type}`}>{currentStage}</span>
                <h2 className="training-title">Biometric Enrollment</h2>
              </div>
              <div className="training-step-card">
                <span className="training-step-label">Step Indicator</span>
                <strong>Sample {currentIndex + 1} of {TOTAL_ROUNDS}</strong>
              </div>
            </div>

            <div className="training-header">
              <div className="progress-wrapper">
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                </div>
                <div className="progress-text">{Math.round(progress)}%</div>
              </div>
            </div>

            <div className="phase-badge-row">
              <span className="prompt-chip">{currentPrompt.label}</span>
              <span className="phase-hint">
                {currentPrompt.type === 'phrase'
                  ? 'Type the phrase exactly as shown.'
                  : 'Type the paragraph naturally at your normal pace.'}
              </span>
            </div>

            <div className={`phrase-box ${currentPrompt.type === 'paragraph' ? 'paragraph-box' : ''}`}>
              <p className="phrase-label">
                {currentPrompt.type === 'phrase' ? 'Type this phrase:' : 'Now type the following paragraph naturally:'}
              </p>
              <p className={`phrase-text ${currentPrompt.type === 'paragraph' ? 'paragraph-text' : ''}`}>{promptText}</p>
            </div>

            <textarea
              ref={inputRef}
              className="input-field"
              placeholder="Click here and start typing..."
              value={typedText}
              onChange={(event) => setTypedText(event.target.value)}
              onKeyDown={handleKeyDown}
              onKeyUp={handleKeyUp}
            />

            <div className="capture-metrics-grid">
              <div className="capture-metric-card">
                <span className="capture-metric-label">Key Press Span</span>
                <strong>{promptMetrics.pressTime > 0 ? `${Math.round((promptMetrics.releaseTime - promptMetrics.pressTime) / 1000)}s` : '--'}</strong>
              </div>
              <div className="capture-metric-card">
                <span className="capture-metric-label">Key Release Time</span>
                <strong>{promptMetrics.releaseTime > 0 ? `${Math.round(promptMetrics.releaseTime % 1000)} ms` : '--'}</strong>
              </div>
              <div className="capture-metric-card">
                <span className="capture-metric-label">Dwell Time</span>
                <strong>{keystrokes.length > 0 ? `${Math.round(promptMetrics.dwellTime)} ms` : '--'}</strong>
              </div>
              <div className="capture-metric-card">
                <span className="capture-metric-label">Flight Time</span>
                <strong>{keystrokes.length > 1 ? `${Math.round(promptMetrics.flightTime)} ms` : '--'}</strong>
              </div>
            </div>

            <div className={`match-status ${isTextMatched ? 'matched' : ''}`}>
              {isTextMatched ? (
                <>
                  <span className="icon">✓</span>
                  <span>Prompt matched. This sample is ready to save.</span>
                </>
              ) : (
                <>
                  <span className="icon">○</span>
                  <span>{typedText.length}/{promptText.length} characters typed</span>
                </>
              )}
            </div>

            <button
              className="btn btn-primary"
              onClick={submitRound}
              disabled={!isTextMatched || loading}
            >
              {loading ? 'Submitting...' : currentIndex + 1 === TOTAL_ROUNDS ? 'Finish Training' : 'Continue'}
            </button>

            {message && <div className="message">{message}</div>}
          </div>
        )}

        {phase === 'completed' && (
          <div className="phase-completed">
            <div className="completion-icon">✓</div>
            <h2>Profile Ready</h2>
            <p>Your phrase and paragraph baseline has been stored. Opening the monitored notepad now.</p>

            <div className="completion-stats">
              <div className="stat">
                <span className="stat-label">Samples Completed</span>
                <span className="stat-value">{TOTAL_ROUNDS}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Phrase Samples</span>
                <span className="stat-value">{lastSummary?.sample_breakdown?.phrase || PHRASE_ROUNDS}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Paragraph Samples</span>
                <span className="stat-value">{lastSummary?.sample_breakdown?.paragraph || PARAGRAPH_ROUNDS}</span>
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
