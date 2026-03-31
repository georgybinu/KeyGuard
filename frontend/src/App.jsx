import { useEffect, useState } from 'react'
import './App.css'
import Auth from './pages/Auth'
import Capture from './pages/Capture'
import Notepad from './pages/Notepad'
import { API_BASE_URL, logoutUser, restoreSession } from './lib/api'

const SESSION_STORAGE_KEY = 'keyguard-session'
const TOTAL_TRAINING_ROUNDS = 13

function App() {
  const [appState, setAppState] = useState('loading')
  const [session, setSession] = useState(null)
  const [statusMessage, setStatusMessage] = useState('Restoring your last session...')

  useEffect(() => {
    const savedToken = window.localStorage.getItem(SESSION_STORAGE_KEY)
    if (!savedToken) {
      setAppState('auth')
      setStatusMessage('')
      return
    }

    restoreSession(savedToken)
      .then((data) => {
        setSession(data)
        setAppState(data.training_completed ? 'notepad' : 'training')
        setStatusMessage('')
      })
      .catch(() => {
        window.localStorage.removeItem(SESSION_STORAGE_KEY)
        setAppState('auth')
        setStatusMessage('')
      })
  }, [])

  const persistSession = (data) => {
    setSession(data)
    window.localStorage.setItem(SESSION_STORAGE_KEY, data.session_token)
  }

  const handleAuthSuccess = (data) => {
    persistSession(data)
    setAppState(data.training_completed ? 'notepad' : 'training')
  }

  const handleTrainingComplete = ({ trainingCompleted, trainingRounds }) => {
    const updatedSession = {
      ...session,
      training_completed: trainingCompleted,
      training_rounds: trainingRounds,
    }
    persistSession(updatedSession)
    setAppState('notepad')
  }

  const handleLogout = async () => {
    if (session?.session_token) {
      try {
        await logoutUser(session.session_token)
      } catch (error) {
        console.error(error)
      }
    }
    window.localStorage.removeItem(SESSION_STORAGE_KEY)
    setSession(null)
    setAppState('auth')
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <p className="app-kicker">Keystroke Dynamics Authentication</p>
            <h1 className="app-logo">KeyGuard</h1>
            <p className="app-tagline">Train once. Type naturally. Surface intruders in real time.</p>
          </div>
          
          {session && (
            <div className="header-nav">
              <div className="header-user">
                <span className="user-name">{session.username}</span>
                <span className={`training-pill ${session.training_completed ? 'ready' : 'pending'}`}>
                  {session.training_completed ? 'Profile ready' : `Training ${session.training_rounds || 0}/${TOTAL_TRAINING_ROUNDS}`}
                </span>
                <button className="logout-btn" onClick={handleLogout}>
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </header>

      <main className="app-main">
        {appState === 'loading' && (
          <section className="loading-panel">
            <h2>Loading KeyGuard</h2>
            <p>{statusMessage}</p>
          </section>
        )}

        {appState === 'auth' && <Auth onSuccess={handleAuthSuccess} />}

        {appState === 'training' && session && (
          <Capture user={session} onComplete={handleTrainingComplete} />
        )}

        {appState === 'notepad' && session && <Notepad session={session} />}
      </main>

      <footer className="app-footer">
        <p>Frontend talks to {API_BASE_URL}</p>
        <p>Sign up, complete phrase and paragraph training, then type in the monitored notepad.</p>
      </footer>
    </div>
  )
}

export default App
