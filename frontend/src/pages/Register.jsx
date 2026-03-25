import React, { useState } from 'react';
import '../styles/Register.css';

function Register({ onSuccess }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!username || !email || !phone || !password) {
      setError('All fields are required');
      setLoading(false);
      return;
    }

    try {
      // Try to register with backend, but also support demo mode
      let response;
      try {
        const params = new URLSearchParams({
          username,
          email,
          phone,
          password
        });
        response = await fetch(`http://localhost:8000/register?${params}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
      } catch (fetchErr) {
        // Demo mode: if backend not available, use local data
        response = { ok: true, json: async () => ({ token: 'demo-token' }) };
      }

      if (response.ok) {
        const data = await response.json?.() || { token: 'demo-token' };
        onSuccess({ 
          username, 
          email, 
          phone,
          registeredAt: new Date().toISOString(),
          token: data.token || 'demo-token' 
        });
      } else {
        setError('Registration failed. Please try again.');
      }
    } catch (err) {
      setError('Connection error. Make sure backend is running on port 8000');
    }

    setLoading(false);
  };

  return (
    <div className="register-container">
      <div className="register-card">
        <div className="register-header">
          <h2>🔐 KeyGuard Registration</h2>
          <p>Create your biometric typing profile</p>
        </div>

        <form onSubmit={handleSubmit} className="register-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="phone">Phone Number</label>
            <input
              id="phone"
              type="tel"
              placeholder="Enter your phone number"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="form-input"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Creating Profile...' : 'Create Profile'}
          </button>
        </form>

        <div className="register-info">
          <h3>What is KeyGuard?</h3>
          <ul>
            <li>✓ Analyzes your unique typing patterns</li>
            <li>✓ Creates your biometric profile</li>
            <li>✓ Detects unauthorized access attempts</li>
            <li>✓ Uses One-Class SVM for anomaly detection</li>
            <li>✓ Measures dwell & flight times</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Register;
