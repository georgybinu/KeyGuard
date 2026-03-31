import { useState } from 'react';
import '../styles/Auth.css';
import { loginUser, registerUser } from '../lib/api';

function Auth({ onSuccess }) {
  const [mode, setMode] = useState('login');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (mode === 'register') {
        if (!username || !email || !phone || !password) {
          setError('All fields are required');
          setLoading(false);
          return;
        }

        if (password !== confirmPassword) {
          setError('Passwords do not match');
          setLoading(false);
          return;
        }

        const data = await registerUser({
          username,
          email,
          phone,
          password,
        });
        onSuccess(data);
      } else {
        if (!username || !password) {
          setError('Username and password are required');
          setLoading(false);
          return;
        }

        const data = await loginUser({
          username,
          password,
        });
        onSuccess(data);
      }
    } catch (err) {
      setError(err.message || 'Connection error. Make sure backend is running.');
    }

    setLoading(false);
  };

  return (
    <div className="auth-stage">
      <div className="auth-panel">
        <div className="auth-tabs">
          <button
            type="button"
            className={`auth-tab ${mode === 'login' ? 'active' : ''}`}
            onClick={() => {
              setMode('login');
              setError('');
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            className={`auth-tab ${mode === 'register' ? 'active' : ''}`}
            onClick={() => {
              setMode('register');
              setError('');
            }}
          >
            Sign Up
          </button>
        </div>

        <div className="auth-copy-block">
          <h2>{mode === 'login' ? 'Welcome Back' : 'Create Your KeyGuard Profile'}</h2>
          <p>
            {mode === 'login'
              ? 'Authenticate with your digital signature.'
              : 'Register, complete training, and enter the monitored workspace.'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-form-stack">
            <div className="auth-field">
              <label>Username</label>
              <input
                type="text"
                placeholder="curator_01"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                disabled={loading}
              />
            </div>

            {mode === 'register' && (
              <>
                <div className="auth-field">
                  <label>Email</label>
                  <input
                    type="email"
                    placeholder="name@example.com"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    disabled={loading}
                  />
                </div>

                <div className="auth-field">
                  <label>Phone</label>
                  <input
                    type="tel"
                    placeholder="+91 98765 43210"
                    value={phone}
                    onChange={(event) => setPhone(event.target.value)}
                    disabled={loading}
                  />
                </div>
              </>
            )}

            <div className="auth-field">
              <label>Secure Password</label>
              <input
                type="password"
                placeholder="••••••••••••"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                disabled={loading}
              />
              {mode === 'login' && (
                <div className="auth-pulse">
                  <div className="auth-pulse-track">
                    <div className="auth-pulse-fill" />
                  </div>
                  <p>Keystroke dynamics sensor active...</p>
                </div>
              )}
            </div>

            {mode === 'register' && (
              <div className="auth-field">
                <label>Confirm Password</label>
                <input
                  type="password"
                  placeholder="••••••••••••"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  disabled={loading}
                />
              </div>
            )}
          </div>

          <div className="auth-actions-row">
            <label className="remember-row">
              <input type="checkbox" disabled={loading} />
              <span>Remember identity</span>
            </label>
            <button type="button" className="text-link" disabled>
              Forgot rhythm?
            </button>
          </div>

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" className="auth-submit" disabled={loading}>
            {loading
              ? mode === 'login'
                ? 'Signing in...'
                : 'Creating account...'
              : mode === 'login'
                ? 'Sign In'
                : 'Create Account'}
          </button>
        </form>

        <div className="auth-divider">
          <span>Or continue with</span>
        </div>

        <div className="auth-provider-grid">
          <button type="button" className="provider-btn">
            <span className="provider-badge">G</span>
            <span>Google</span>
          </button>
          <button type="button" className="provider-btn">
            <span className="provider-badge">P</span>
            <span>Passkey</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default Auth;
