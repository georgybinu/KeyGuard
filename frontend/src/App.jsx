import { useState } from 'react'
import './App.css'
import Auth from './pages/Auth'
import Capture from './pages/Capture'
import TestCases from './pages/TestCases'
import Dashboard from './pages/Dashboard'

const BACKEND_URL = 'http://localhost:8000'

function App() {
  // Global state
  const [currentPage, setCurrentPage] = useState('register') // register, capture, test-cases, dashboard
  const [user, setUser] = useState(null) // { username, email, phone, registeredAt }
  const [trainingComplete, setTrainingComplete] = useState(false)
  const [userProfile, setUserProfile] = useState(null)
  const [testResults, setTestResults] = useState([])


  // Handle user registration
  const handleRegisterSuccess = (userData) => {
    setUser(userData)
    setCurrentPage('capture')
    setUserProfile({
      username: userData.username,
      email: userData.email,
      phone: userData.phone,
      registeredAt: new Date(userData.registeredAt).toLocaleDateString(),
      profileStatus: 'Pending Training',
      trainingRoundsCompleted: 0,
      totalTrainingRounds: 10,
      detectionAccuracy: 0,
      totalTests: 0,
      successfulTests: 0
    })
  }

  // Handle capture training completion
  const handleCaptureComplete = (captureData) => {
    setTrainingComplete(true)
    setUserProfile(prev => ({
      ...prev,
      trainingRoundsCompleted: 10,
      profileStatus: 'Trained & Ready',
      profileFeatures: captureData.features
    }))
    // Auto-navigate to test cases after a short delay
    setTimeout(() => {
      setCurrentPage('test-cases')
    }, 2000)
  }

  // Handle test case results
  const handleTestResult = (result) => {
    setTestResults(prev => [...prev, result])
    
    // Update user profile with test statistics
    setUserProfile(prev => {
      const total = prev.totalTests + 1
      const successful = prev.successfulTests + (result.passed ? 1 : 0)
      return {
        ...prev,
        totalTests: total,
        successfulTests: successful,
        detectionAccuracy: total > 0 ? Math.round((successful / total) * 100) : 0
      }
    })
  }

  // Handle logout
  const handleLogout = () => {
    setUser(null)
    setTrainingComplete(false)
    setUserProfile(null)
    setTestResults([])
    setCurrentPage('register')
  }

  // Navigation handler
  const navigateTo = (page) => {
    if (page === 'register') {
      handleLogout()
    } else if (page === 'capture' && !user) {
      alert('Please register first!')
      return
    } else if ((page === 'test-cases' || page === 'dashboard') && !trainingComplete) {
      alert('Please complete training first!')
      return
    }
    setCurrentPage(page)
  }

  return (
    <div className="app">
      {/* Header Navigation */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <h1 className="app-logo">🔐 KeyGuard</h1>
            <p className="app-tagline">Keystroke Authentication System</p>
          </div>
          
          {user && (
            <div className="header-nav">
              <nav className="nav-menu">
                <button 
                  className={`nav-item ${currentPage === 'capture' ? 'active' : ''}`}
                  onClick={() => navigateTo('capture')}
                >
                  Training
                </button>
                {trainingComplete && (
                  <>
                    <button 
                      className={`nav-item ${currentPage === 'test-cases' ? 'active' : ''}`}
                      onClick={() => navigateTo('test-cases')}
                    >
                      Test Cases
                    </button>
                    <button 
                      className={`nav-item ${currentPage === 'dashboard' ? 'active' : ''}`}
                      onClick={() => navigateTo('dashboard')}
                    >
                      Dashboard
                    </button>
                  </>
                )}
              </nav>
              
              <div className="header-user">
                <span className="user-name">👤 {user.username}</span>
                <button 
                  className="logout-btn"
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        {currentPage === 'register' && (
          <Auth onSuccess={handleRegisterSuccess} />
        )}
        
        {currentPage === 'capture' && user && (
          <Capture 
            user={user}
            onComplete={handleCaptureComplete}
          />
        )}
        
        {currentPage === 'test-cases' && user && trainingComplete && (
          <TestCases 
            user={user}
            onTestResult={handleTestResult}
          />
        )}
        
        {currentPage === 'dashboard' && user && userProfile && (
          <Dashboard 
            user={user}
            profile={userProfile}
            testResults={testResults}
            onLogout={handleLogout}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>KeyGuard &copy; 2024 - Keystroke Authentication Demo</p>
        <p>Backend: {BACKEND_URL}</p>
      </footer>
    </div>
  )
}

export default App
