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
    <div className="capture-stage">
      {phase === 'ready' && (
        <div className="training-intro">
          <div className="intro-container">
            <h1 className="intro-title">Keystroke Training</h1>
            <p className="intro-description">
              Complete this training to establish your unique typing signature. This helps KeyGuard recognize your authentic keystrokes.
            </p>
            <button className="intro-btn" onClick={startTraining}>
              Begin Training
            </button>
          </div>
        </div>
      )}

      {phase === 'training' && currentPrompt && (
        <div className="training-active">
          <div className="training-header-bar">
            <div className="progress-wrapper">
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progress}%` }}></div>
              </div>
            </div>
          </div>

          <div className="training-content">
            <div className="phrase-display">
              <p className="phrase-text">{promptText}</p>
            </div>

            <textarea
              ref={inputRef}
              className="training-input"
              placeholder="Start typing the phrase above"
              value={typedText}
              onChange={(event) => setTypedText(event.target.value)}
              onKeyDown={handleKeyDown}
              onKeyUp={handleKeyUp}
              disabled={loading}
            />

            {message && <div className="training-message">{message}</div>}

            <div className="training-stats">
              <div className="stat-item">
                <span className="stat-label">Keystrokes</span>
                <span className="stat-value">{keystrokes.length}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Progress</span>
                <span className="stat-value">{Math.round(progress)}%</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Round</span>
                <span className="stat-value">{currentIndex + 1}/{TOTAL_ROUNDS}</span>
              </div>
            </div>

            <button
              className="training-btn"
              onClick={submitRound}
              disabled={!isTextMatched || loading}
            >
              {loading ? 'Submitting...' : currentIndex + 1 === TOTAL_ROUNDS ? 'Finish Training' : 'Continue'}
            </button>
          </div>
        </div>
      )}

      {phase === 'completed' && (
        <div className="training-completed">
          <div className="completion-container">
            <div className="completion-icon">✓</div>
            <h2>Training Complete</h2>
            <p>Your keystroke signature has been established. Redirecting to your secure workspace...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default Capture;
