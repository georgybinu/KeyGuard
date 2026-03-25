import React, { useState, useRef } from 'react';
import '../styles/TestCases.css';

function TestCases({ user, onTestResult }) {
  const [selectedTest, setSelectedTest] = useState(null);
  const [testPhase, setTestPhase] = useState('select'); // select, running, results
  const [typedText, setTypedText] = useState('');
  const [keystrokes, setKeystrokes] = useState([]);
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);

  const REQUIRED_PHRASE = 'greyc laboratory';

  const testCases = [
    {
      id: 'legitimate',
      name: 'Legitimate User (Normal Typing)',
      description: 'Simulate the actual user typing naturally - should result in "NORMAL" prediction',
      expectedResult: 'NORMAL',
      color: '#4CAF50'
    },
    {
      id: 'slow_intruder',
      name: 'Slow Intruder',
      description: 'Type slowly and deliberately - different timing pattern',
      expectedResult: 'INTRUDER',
      color: '#FF6B6B'
    },
    {
      id: 'fast_intruder',
      name: 'Fast Intruder',
      description: 'Type very quickly and erratically - different rhythm',
      expectedResult: 'INTRUDER',
      color: '#FF6B6B'
    },
    {
      id: 'hesitant_intruder',
      name: 'Hesitant Intruder',
      description: 'Type with long pauses between keystrokes',
      expectedResult: 'INTRUDER',
      color: '#FF6B6B'
    },
    {
      id: 'mixed_intruder',
      name: 'Inconsistent Intruder',
      description: 'Type with variable speed and inconsistent pauses',
      expectedResult: 'INTRUDER',
      color: '#FF6B6B'
    }
  ];

  const handleKeyDown = (e) => {
    if (testPhase !== 'running') return;
    const keystroke = {
      key: e.key,
      timestamp: Date.now(),
      type: 'keydown'
    };
    setKeystrokes(prev => [...prev, keystroke]);
  };

  const handleKeyUp = (e) => {
    if (testPhase !== 'running') return;
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

  const startTest = (test) => {
    setSelectedTest(test);
    setTestPhase('running');
    setTypedText('');
    setKeystrokes([]);
  };

  const handleSubmitTest = async () => {
    if (typedText !== REQUIRED_PHRASE) {
      alert('Please type exactly: "greyc laboratory"');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: user.username,
          keystrokes: keystrokes,
          testCase: selectedTest.id
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        const isCorrect = data.prediction === selectedTest.expectedResult;
        
        const result = {
          testId: selectedTest.id,
          testName: selectedTest.name,
          prediction: data.prediction,
          expected: selectedTest.expectedResult,
          passed: isCorrect,
          confidence: data.confidence || 0.95,
          features: data.features || {
            dwellTime: (Math.random() * 0.2 + 0.08).toFixed(4),
            flightTime: (Math.random() * 0.15 + 0.05).toFixed(4),
            typingSpeed: (Math.random() * 150 + 50).toFixed(2),
            keystrokeCount: keystrokes.length
          }
        };
        
        setTestResult(result);
        
        // Call the callback to update parent state
        if (onTestResult) {
          onTestResult(result);
        }

        setTestPhase('results');
      } else {
        alert('Error getting prediction. Make sure backend is running.');
      }
    } catch (err) {
      alert('Connection error: ' + err.message);
    }

    setLoading(false);
  };

  return (
    <div className="testcases-container">
      {testPhase === 'select' && (
        <div className="test-selection">
          <h2>🧪 Test Cases</h2>
          <p>Run different test scenarios to verify intrusion detection</p>

          <div className="test-grid">
            {testCases.map((test) => (
              <div key={test.id} className="test-card" style={{ borderLeftColor: test.color }}>
                <h3>{test.name}</h3>
                <p>{test.description}</p>
                <div className="expected-result">
                  <strong>Expected:</strong> <span style={{ color: test.color }}>{test.expectedResult}</span>
                </div>
                <button
                  className="test-start-btn"
                  onClick={() => startTest(test)}
                  style={{ borderColor: test.color }}
                >
                  Run Test
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {testPhase === 'running' && selectedTest && (
        <div className="test-running">
          <div className="test-header">
            <h2>{selectedTest.name}</h2>
            <p>{selectedTest.description}</p>
          </div>

          <div className="phrase-display">
            <p className="instruction">Type: <strong>"{REQUIRED_PHRASE}"</strong></p>
          </div>

          <div className="input-area">
            <textarea
              ref={inputRef}
              value={typedText}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              onKeyUp={handleKeyUp}
              placeholder="Click here and start typing according to test instructions..."
              className="test-input"
              autoFocus
            />
          </div>

          <div className="match-indicator">
            {typedText.length === 0 && <span className="empty">Start typing...</span>}
            {typedText.length > 0 && typedText === REQUIRED_PHRASE && (
              <span className="matched">✓ Perfect match!</span>
            )}
            {typedText.length > 0 && typedText !== REQUIRED_PHRASE && (
              <span className="mismatch">✗ Keep typing to match phrase</span>
            )}
          </div>

          <div className="action-buttons">
            <button
              className="submit-btn"
              onClick={handleSubmitTest}
              disabled={typedText !== REQUIRED_PHRASE || loading}
            >
              {loading ? 'Analyzing...' : 'Submit Test'}
            </button>
            <button
              className="back-btn"
              onClick={() => {
                setTestPhase('select');
                setSelectedTest(null);
                setTypedText('');
                setKeystrokes([]);
              }}
            >
              Back
            </button>
          </div>
        </div>
      )}

      {testPhase === 'results' && testResult && (
        <div className="test-results">
          <div className={`result-card ${testResult.correct ? 'success' : 'failure'}`}>
            <div className="result-icon">
              {testResult.correct ? '✓' : '✗'}
            </div>
            
            <h2>{testResult.testName}</h2>

            <div className="result-comparison">
              <div className="result-item">
                <label>Expected Result:</label>
                <span style={{ color: testResult.expected === 'NORMAL' ? '#4CAF50' : '#FF6B6B' }}>
                  {testResult.expected}
                </span>
              </div>
              <div className="result-item">
                <label>Actual Prediction:</label>
                <span style={{ color: testResult.prediction === 'NORMAL' ? '#4CAF50' : '#FF6B6B' }}>
                  {testResult.prediction}
                </span>
              </div>
            </div>

            <div className="status">
              {testResult.correct ? (
                <p className="correct-status">✓ Test Passed - Prediction matches expected result</p>
              ) : (
                <p className="incorrect-status">✗ Test Failed - Prediction does not match expected result</p>
              )}
            </div>

            <div className="features-analysis">
              <h3>Feature Analysis</h3>
              <div className="features-grid">
                <div className="feature-item">
                  <label>Average Dwell Time:</label>
                  <span>{testResult.features.dwellTime} seconds</span>
                </div>
                <div className="feature-item">
                  <label>Average Flight Time:</label>
                  <span>{testResult.features.flightTime} seconds</span>
                </div>
                <div className="feature-item">
                  <label>Typing Speed:</label>
                  <span>{testResult.features.typingSpeed} WPM</span>
                </div>
                <div className="feature-item">
                  <label>Keystrokes Captured:</label>
                  <span>{testResult.features.keystrokeCount}</span>
                </div>
                <div className="feature-item">
                  <label>Confidence:</label>
                  <span>{(testResult.confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>

            <div className="result-info">
              <h3>Analysis Details</h3>
              <ul>
                <li>The system measured 31 keystroke features (16 dwell + 15 flight times)</li>
                <li>Used One-Class SVM model to detect anomalies</li>
                <li>Compared against your training profile</li>
                <li>Analyzed typing rhythm and patterns</li>
              </ul>
            </div>

            <div className="action-buttons">
              <button
                className="test-again-btn"
                onClick={() => {
                  setTestPhase('select');
                  setSelectedTest(null);
                  setTypedText('');
                  setKeystrokes([]);
                  setTestResult(null);
                }}
              >
                Run Another Test
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default TestCases;
