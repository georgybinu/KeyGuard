import { useState, useRef, useEffect } from 'react'
import './App.css'

const PARAGRAPH = "I start my day with a cup of tea and check my phone for a few minutes. It is a simple routine, but it helps me get ready for the day."
const BACKEND_URL = 'http://localhost:8000'
const COLLECTION_PARAGRAPHS = [
  "I start my day with a cup of tea and check my phone for a few minutes. It is a simple routine, but it helps me get ready for the day.",
  "The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet at least once.",
  "Keystroke dynamics can be used to verify user identity. The way we type is unique to each person, like a fingerprint."
]

function App() {
  // Phase management
  const [phase, setPhase] = useState('setup') // setup, collecting, training, detecting
  
  // Session info
  const [username, setUsername] = useState('')
  const [sessionToken, setSessionToken] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  
  // Collection phase
  const [currentParagraphIndex, setCurrentParagraphIndex] = useState(0)
  const [typed, setTyped] = useState('')
  const [keystrokes, setKeystrokes] = useState([])
  const [keystrokeBuffer, setKeystrokeBuffer] = useState([])
  const [collectionProgress, setCollectionProgress] = useState(0) // 0, 1, 2 for 3 paragraphs
  const activeKeysRef = useRef({})
  
  // Training phase
  const [trainingStatus, setTrainingStatus] = useState('')
  
  // Detection phase
  const [predictionResult, setPredictionResult] = useState(null)
  
  // UI state
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Get current paragraph
  const currentParagraph = COLLECTION_PARAGRAPHS[collectionProgress]
  const isComplete = typed === currentParagraph
  const progress = Math.round((typed.length / currentParagraph.length) * 100)

  // Start session - moves to COLLECTION phase
  const startSession = async () => {
    if (!username.trim()) {
      setError('Please enter a username')
      return
    }
    
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`${BACKEND_URL}/capture/start?username=${encodeURIComponent(username)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (!response.ok) throw new Error('Failed to start session')
      
      const data = await response.json()
      setSessionToken(data.session_token)
      setSessionId(data.session_id)
      setPhase('collecting')
      setPredictionResult(null)
      setError(null)
    } catch (err) {
      setError(`Failed to connect: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  // Move to next paragraph in collection or finish collection
  const nextCollection = async () => {
    if (collectionProgress < 2) {
      // Move to next paragraph
      setCollectionProgress(collectionProgress + 1)
      setTyped('')
      setKeystrokeBuffer([])
    } else {
      // Finished collecting all 3 paragraphs - move to TRAINING phase
      await moveToTraining()
    }
  }

  // Move to TRAINING phase
  const moveToTraining = async () => {
    try {
      setPhase('training')
      setTrainingStatus('Training model...')
      
      // Send all collected keystrokes to train endpoint
      const transformedKeystrokes = keystrokes.map(k => ({
        key: k.key,
        key_press_time: k.keydown,
        key_release_time: k.keyup
      }))

      const response = await fetch(
        `${BACKEND_URL}/train?username=${encodeURIComponent(username)}&session_token=${sessionToken}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(transformedKeystrokes)
        }
      )
      
      if (!response.ok) throw new Error('Training failed')
      
      const result = await response.json()
      setTrainingStatus(`Training complete! Profile ready for ${result.username}`)
      
      // After 2 seconds, move to DETECTING phase
      setTimeout(() => {
        setPhase('detecting')
        setTyped('')
        setKeystrokeBuffer([])
        setPredictionResult(null)
      }, 2000)
    } catch (err) {
      setError(`Training error: ${err.message}`)
      setTrainingStatus('Training failed')
    }
  }

  // Send keystrokes for DETECTION (only in detecting phase)
  const sendPrediction = async (keystrokeData) => {
    if (phase !== 'detecting' || !sessionToken || keystrokeData.length === 0) return
    
    try {
      const response = await fetch(
        `${BACKEND_URL}/predict?username=${encodeURIComponent(username)}&session_token=${sessionToken}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(keystrokeData)
        }
      )
      
      if (!response.ok) throw new Error('Prediction failed')
      
      const result = await response.json()
      setPredictionResult(result)
    } catch (err) {
      console.error('Prediction error:', err)
    }
  }

  // Transform keystroke data to backend format
  const transformKeystroke = (keystroke) => {
    return {
      key: keystroke.key,
      key_press_time: keystroke.keydown,
      key_release_time: keystroke.keyup
    }
  }

  // Handle keydown - works in both collection and detecting phases
  const handleKeyDown = (e) => {
    if (phase !== 'collecting' && phase !== 'detecting') {
      e.preventDefault()
      return
    }
    
    const key = e.key
    const timestamp = performance.now()
    
    if (!activeKeysRef.current[key]) {
      activeKeysRef.current[key] = timestamp
    }
  }

  // Handle keyup - works in both collection and detecting phases
  const handleKeyUp = (e) => {
    if (phase !== 'collecting' && phase !== 'detecting') return
    
    const key = e.key
    const keyupTimestamp = performance.now()
    const keydownTimestamp = activeKeysRef.current[key]

    if (keydownTimestamp !== undefined) {
      const keystrokeEvent = {
        key: key,
        keydown: Math.round(keydownTimestamp),
        keyup: Math.round(keyupTimestamp)
      }

      setKeystrokes(prev => [...prev, keystrokeEvent])
      const newBuffer = [...keystrokeBuffer, keystrokeEvent]
      setKeystrokeBuffer(newBuffer)
      
      delete activeKeysRef.current[key]
      
      // In DETECTING phase: send batch prediction every 5 keystrokes
      // In COLLECTION phase: just store (no predictions)
      if (phase === 'detecting' && newBuffer.length >= 5) {
        const transformedKeystrokes = newBuffer.map(k => ({
          key: k.key,
          key_press_time: k.keydown,
          key_release_time: k.keyup
        }))
        sendPrediction(transformedKeystrokes)
        setKeystrokeBuffer([])
      }
    }
  }

  // Handle input change
  const handleInputChange = (e) => {
    setTyped(e.target.value)
  }

  // End session with backend
  const endSession = async () => {
    if (!sessionToken) return
    
    try {
      await fetch(
        `${BACKEND_URL}/capture/end?username=${encodeURIComponent(username)}&session_token=${sessionToken}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        }
      )
    } catch (err) {
      console.error('Error ending session:', err)
    }
  }

  // Reset everything
  const handleReset = async () => {
    await endSession()
    setPhase('setup')
    setUsername('')
    setSessionToken(null)
    setSessionId(null)
    setTyped('')
    setKeystrokes([])
    setKeystrokeBuffer([])
    setCollectionProgress(0)
    setPredictionResult(null)
    setTrainingStatus('')
    setError(null)
    activeKeysRef.current = {}
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">KeyGuard</h1>
        <p className="app-subtitle">Keystroke Authentication - 3-Phase Setup</p>
        {phase !== 'setup' && (
          <div className="phase-indicator">
            Phase: <strong>{phase.toUpperCase()}</strong> | User: <strong>{username}</strong>
          </div>
        )}
      </header>

      <main className="app-main">
        {/* PHASE 1: SETUP - Username Input */}
        {phase === 'setup' && (
          <div className="session-setup">
            <h2 className="setup-title">🔐 Create Your Keystroke Profile</h2>
            <p className="setup-subtitle">
              3-phase process: Collect → Train → Detect
            </p>
            <div className="setup-form">
              <input
                type="text"
                className="username-input"
                placeholder="Enter your username..."
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && startSession()}
                disabled={loading}
                autoFocus
              />
              <button 
                className="action-btn primary"
                onClick={startSession}
                disabled={loading || !username.trim()}
              >
                {loading ? 'Connecting...' : 'Start Profile Creation'}
              </button>
            </div>
            {error && <div className="error-message">{error}</div>}
            <div className="phase-explanation">
              <h3>How it works:</h3>
              <p>✍️ <strong>Phase 1 (Collection):</strong> Type 3 paragraphs at your normal speed. We'll collect your keystroke patterns.</p>
              <p>🤖 <strong>Phase 2 (Training):</strong> Your profile is trained on the collected data. This is your unique fingerprint.</p>
              <p>🛡️ <strong>Phase 3 (Detection):</strong> Type normally and we'll detect if it's really you or an intruder.</p>
            </div>
          </div>
        )}

        {/* PHASE 2: COLLECTION - Collect Keystroke Data */}
        {phase === 'collecting' && (
          <>
            <div className="phase-header">
              <h2>📝 Phase 1: Collect Your Keystroke Signature</h2>
              <p>Type the following paragraphs. Just collect mode - NO predictions yet!</p>
            </div>

            <div className="collection-progress-wrapper">
              <div className="collection-steps">
                {[0, 1, 2].map((step) => (
                  <div
                    key={step}
                    className={`step ${step === collectionProgress ? 'active' : ''} ${step < collectionProgress ? 'completed' : ''}`}
                  >
                    <div className="step-number">{step + 1}</div>
                    <div className="step-label">Paragraph {step + 1}</div>
                  </div>
                ))}
              </div>
              <p className="collection-status">
                Collecting: Paragraph {collectionProgress + 1} of 3
              </p>
            </div>

            {/* Paragraph Display */}
            <div className="paragraph-section">
              <div className="paragraph-display">
                {currentParagraph}
              </div>
            </div>

            {/* Input Box */}
            <div className="input-section">
              <input
                type="text"
                className="typing-input collection-input"
                placeholder="Start typing here (just collecting, no predictions)..."
                value={typed}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                onKeyUp={handleKeyUp}
                disabled={isComplete}
                autoFocus
              />
            </div>

            {/* Progress Bar */}
            <div className="progress-section">
              <div className="progress-bar-wrapper">
                <div className="progress-bar" style={{ width: `${progress}%` }}></div>
              </div>
              <p className="progress-text">Progress: {progress}%</p>
              <p className="keystroke-count">Keystrokes collected: {keystrokes.length}</p>
            </div>

            {/* Status */}
            <div className="status-section">
              {isComplete ? (
                <div className="status-card completed">
                  <h2 className="status-title">✓ Paragraph Complete!</h2>
                  <p className="status-message">
                    Great! You typed it correctly in {keystrokeBuffer.length} more keystrokes.
                  </p>
                </div>
              ) : (
                <div className="status-card typing">
                  <p className="status-message">
                    Keep typing...
                  </p>
                </div>
              )}
            </div>

            {/* Next Button */}
            {isComplete && (
              <div className="actions-section">
                <button 
                  className="action-btn primary"
                  onClick={nextCollection}
                >
                  {collectionProgress < 2 ? `Next Paragraph` : 'Move to Training'}
                </button>
              </div>
            )}

            {error && <div className="error-message">{error}</div>}
          </>
        )}

        {/* PHASE 3: TRAINING - Train ML Model */}
        {phase === 'training' && (
          <div className="training-phase">
            <div className="phase-header">
              <h2>🤖 Phase 2: Training Your Profile</h2>
            </div>
            <div className="training-box">
              <div className="training-spinner"></div>
              <p className="training-status">{trainingStatus}</p>
              <p className="training-details">
                Processing {keystrokes.length} keystrokes from {collectionProgress + 1} paragraphs...
              </p>
            </div>
            {error && <div className="error-message">{error}</div>}
          </div>
        )}

        {/* PHASE 4: DETECTION - Make Predictions */}
        {phase === 'detecting' && (
          <>
            <div className="phase-header">
              <h2>🛡️ Phase 3: Intrusion Detection Active</h2>
              <p>Type normally. Your profile is now trained and ready to detect if it's really you!</p>
            </div>

            {/* Input Box */}
            <div className="input-section">
              <input
                type="text"
                className="typing-input detecting-input"
                placeholder="Type freely (predictions every 5 keystrokes)..."
                value={typed}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                onKeyUp={handleKeyUp}
                autoFocus
              />
            </div>

            {/* Keystroke Counter */}
            <div className="keystroke-counter">
              <p>Keystrokes: {keystrokes.length} | Buffer: {keystrokeBuffer.length}</p>
            </div>

            {/* Intrusion Detection Result */}
            {predictionResult && (
              <div className={`prediction-card ${predictionResult.decision}`}>
                <h3 className="prediction-title">🔍 Detection Result</h3>
                <div className="prediction-content">
                  <div className="decision-display">
                    <p className="decision-label">Authentication Decision:</p>
                    <p className={`decision-value ${predictionResult.decision}`}>
                      {predictionResult.decision === 'normal' && '✅ LEGITIMATE USER'}
                      {predictionResult.decision === 'suspicious' && '⚠️ SUSPICIOUS ACTIVITY'}
                      {predictionResult.decision === 'intrusion' && '🚨 INTRUSION DETECTED'}
                    </p>
                  </div>
                  <div className="confidence-display">
                    <p className="confidence-label">Confidence Scores:</p>
                    <div className="confidence-scores">
                      <span>RF Model: {(predictionResult.confidence.rf_probability * 100).toFixed(1)}%</span>
                      <span>SVM Model: {(predictionResult.confidence.svm_anomaly_score * 100).toFixed(1)}%</span>
                      <span>Overall: {(predictionResult.confidence.overall_confidence * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="actions-section">
              <button 
                className="action-btn secondary" 
                onClick={handleReset}
              >
                Start Over
              </button>
            </div>

            {error && <div className="error-message">{error}</div>}
          </>
        )}
      </main>
    </div>
  )
}

export default App
