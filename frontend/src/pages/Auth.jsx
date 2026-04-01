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
  const [showPassword, setShowPassword] = useState(false);

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
      {/* Background pattern */}
      <div className="auth-bg-pattern">
        <div className="auth-bg-glow auth-glow-1"></div>
        <div className="auth-bg-glow auth-glow-2"></div>
      </div>

      <div className="auth-container">
        {/* Header with Shield Icon */}
        <div className="auth-header">
          <div className="shield-icon">
            <svg width="32" height="32" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M32 4L12 14V28C12 44 32 56 32 56C32 56 52 44 52 28V14L32 4Z" stroke="currentColor" strokeWidth="2" fill="none"/>
            </svg>
          </div>
          <h1 className="auth-title">KeyGuard</h1>
          <p className="auth-subtitle">Keystroke Dynamics Authentication</p>
        </div>

        {/* Auth Panel Card */}
        <div className="glass-card auth-panel">
          {/* Tabs */}
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

          {/* Error Message */}
          {error && (
            <div className="auth-error animate-fade-in">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="auth-form">
            <div className="auth-form-stack">
              {/* Username */}
              <div className="auth-field">
                <div className="auth-input-wrapper">
                  <svg className="auth-input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M10 10C12.21 10 14 8.21 14 6C14 3.79 12.21 2 10 2C7.79 2 6 3.79 6 6C6 8.21 7.79 10 10 10ZM10 12C7.67 12 3 13.17 3 15.5V18H17V15.5C17 13.17 12.33 12 10 12Z" fill="currentColor"/>
                  </svg>
                  <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(event) => setUsername(event.target.value)}
                    disabled={loading}
                    className="auth-input"
                  />
                </div>
              </div>

              {/* Email (Register only) */}
              {mode === 'register' && (
                <div className="auth-field">
                  <div className="auth-input-wrapper">
                    <svg className="auth-input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <path d="M3 4C3 3.4 3.4 3 4 3H16C16.6 3 17 3.4 17 4V4L10 8.46L3 4V4ZM3 5.46V16C3 16.6 3.4 17 4 17H16C16.6 17 17 16.6 17 16V5.46L10 10L3 5.46Z" fill="currentColor"/>
                    </svg>
                    <input
                      type="email"
                      placeholder="Email address"
                      value={email}
                      onChange={(event) => setEmail(event.target.value)}
                      disabled={loading}
                      className="auth-input"
                    />
                  </div>
                </div>
              )}

              {/* Phone (Register only) */}
              {mode === 'register' && (
                <div className="auth-field">
                  <div className="auth-input-wrapper">
                    <svg className="auth-input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <path d="M5 2C3.34 2 2 3.34 2 5V15C2 16.66 3.34 18 5 18H15C16.66 18 18 16.66 18 15V5C18 3.34 16.66 2 15 2H5ZM5 4H15C15.55 4 16 4.45 16 5V15C16 15.55 15.55 16 15 16H5C4.45 16 4 15.55 4 15V5C4 4.45 4.45 4 5 4ZM7 6H9V9H7V6ZM10 10H13V12H10V10Z" fill="currentColor"/>
                    </svg>
                    <input
                      type="tel"
                      placeholder="Phone (optional)"
                      value={phone}
                      onChange={(event) => setPhone(event.target.value)}
                      disabled={loading}
                      className="auth-input"
                    />
                  </div>
                </div>
              )}

              {/* Password */}
              <div className="auth-field">
                <div className="auth-input-wrapper">
                  <svg className="auth-input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M16 8H7V5C7 2.79 5.66 1 4 1C2.34 1 1 2.79 1 5V14C1 15.66 2.34 17 4 17H16C17.66 17 19 15.66 19 14V10C19 8.34 17.66 8 16 8ZM5 14C4.45 14 4 13.55 4 13C4 12.45 4.45 12 5 12C5.55 12 6 12.45 6 13C6 13.55 5.55 14 5 14Z" fill="currentColor"/>
                  </svg>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    disabled={loading}
                    className="auth-input"
                  />
                  <button
                    type="button"
                    className="auth-eye-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={loading}
                  >
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <path d="M10 4C5.59 4 1.95 6.61 1 10c.95 3.39 4.59 6 9 6s8.05-2.61 9-6c-.95-3.39-4.59-6-9-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z" fill="currentColor"/>
                    </svg>
                  </button>
                </div>
              </div>

              {/* Confirm Password (Register only) */}
              {mode === 'register' && (
                <div className="auth-field">
                  <div className="auth-input-wrapper">
                    <svg className="auth-input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <path d="M16 8H7V5C7 2.79 5.66 1 4 1C2.34 1 1 2.79 1 5V14C1 15.66 2.34 17 4 17H16C17.66 17 19 15.66 19 14V10C19 8.34 17.66 8 16 8ZM5 14C4.45 14 4 13.55 4 13C4 12.45 4.45 12 5 12C5.55 12 6 12.45 6 13C6 13.55 5.55 14 5 14Z" fill="currentColor"/>
                    </svg>
                    <input
                      type="password"
                      placeholder="Confirm Password"
                      value={confirmPassword}
                      onChange={(event) => setConfirmPassword(event.target.value)}
                      disabled={loading}
                      className="auth-input"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Submit Button */}
            <button type="submit" className="gradient-button auth-submit" disabled={loading}>
              {loading
                ? mode === 'login'
                  ? 'Signing in...'
                  : 'Creating account...'
                : mode === 'login'
                ? 'Sign In'
                : 'Create Account'}
            </button>
          </form>

          {/* Divider */}
          <div className="auth-divider">
            <span>or continue with</span>
          </div>

          {/* OAuth Buttons */}
          <div className="auth-oauth">
            <button type="button" className="oauth-btn" disabled={loading}>
              Google
            </button>
            <button type="button" className="oauth-btn" disabled={loading}>
              Microsoft
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Auth;
