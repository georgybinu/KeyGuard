import React, { useState } from 'react';
import '../styles/Auth.css';

function Auth({ onSuccess }) {
  const [mode, setMode] = useState('login'); // login or register
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (mode === 'register') {
        // Register validation
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

        // Register user
        const params = new URLSearchParams({
          username,
          email,
          phone,
          password
        });
        const response = await fetch(`http://localhost:8000/register?${params}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
          const data = await response.json();
          onSuccess({
            username,
            email,
            phone,
            registeredAt: new Date().toISOString(),
            token: data.token || 'demo-token',
            isNewUser: true
          });
        } else {
          setError('Registration failed. Username might already exist.');
        }
      } else {
        // Login validation
        if (!username || !password) {
          setError('Username and password are required');
          setLoading(false);
          return;
        }

        // For demo: accept any username/password combination
        // In production, would verify against backend
        onSuccess({
          username,
          email: `${username}@keyguard.local`,
          phone: 'Not provided',
          registeredAt: new Date().toISOString(),
          token: 'login-token-' + Date.now(),
          isNewUser: false
        });
      }
    } catch (err) {
      setError('Connection error. Make sure backend is running.');
    }

    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>🔐 KeyGuard</h1>
          <p>Keystroke Authentication</p>
        </div>

        <div className="auth-tabs">
          <button
            className={`tab ${mode === 'login' ? 'active' : ''}`}
            onClick={() => {
              setMode('login');
              setError('');
            }}
          >
            Sign In
          </button>
          <button
            className={`tab ${mode === 'register' ? 'active' : ''}`}
            onClick={() => {
              setMode('register');
              setError('');
            }}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              placeholder="Enter username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
            />
          </div>

          {mode === 'register' && (
            <>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  placeholder="Enter email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label>Phone</label>
                <input
                  type="tel"
                  placeholder="Enter phone"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  disabled={loading}
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Enter password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
            />
          </div>

          {mode === 'register' && (
            <div className="form-group">
              <label>Confirm Password</label>
              <input
                type="password"
                placeholder="Confirm password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={loading}
              />
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading
              ? mode === 'login'
                ? 'Signing in...'
                : 'Creating account...'
              : mode === 'login'
              ? 'Sign In'
              : 'Create Account'}
          </button>
        </form>

        <div className="auth-info">
          <div className="info-item">
            <span className="icon">⌨️</span>
            <span>Keystroke biometric authentication</span>
          </div>
          <div className="info-item">
            <span className="icon">🎯</span>
            <span>Train your unique typing pattern</span>
          </div>
          <div className="info-item">
            <span className="icon">🛡️</span>
            <span>Real-time intrusion detection</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Auth;
