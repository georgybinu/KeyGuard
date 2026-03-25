import React, { useState, useEffect } from 'react';
import '../styles/Dashboard.css';

function Dashboard({ user, profile, testResults, onLogout }) {
  const [stats, setStats] = useState(profile || null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Use passed profile or fetch stats from backend
    if (profile) {
      setStats(profile);
    } else {
      fetchStats();
    }
  }, [profile]);

  const fetchStats = async () => {
    try {
      const response = await fetch(`http://localhost:8000/user/${user.username}/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      } else {
        // Use mock data if endpoint doesn't exist
        setStats(getMockStats());
      }
    } catch (err) {
      setStats(getMockStats());
    }
    setLoading(false);
  };

  const getMockStats = () => ({
    username: user.username,
    email: user.email,
    phone: user.phone,
    registeredAt: user.registeredAt,
    profileStatus: 'Active',
    trainingRoundsCompleted: 10,
    totalTrainingRounds: 10,
    totalTests: testResults?.length || 0,
    successfulTests: testResults?.filter(t => t.passed)?.length || 0,
    detectionAccuracy: testResults?.length > 0 ? Math.round((testResults.filter(t => t.passed).length / testResults.length) * 100) : 0,
    profileFeatures: {
      avgDwellTime: 0.12,
      avgFlightTime: 0.08,
      typingSpeed: 75,
      keystrokeCount: 160
    },
    recentActivity: testResults?.map((t, i) => ({
      id: i,
      action: t.testName,
      result: t.passed ? 'PASSED' : 'FAILED',
      time: new Date().toLocaleTimeString()
    })) || []
  });

  if (loading) {
    return <div className="dashboard-container"><p>Loading dashboard...</p></div>;
  }

  return (
    <div className="dashboard-container">
      <h2>📊 User Dashboard</h2>

      <div className="dashboard-grid">
        {/* User Profile Card */}
        <div className="card profile-card">
          <h3>👤 User Profile</h3>
          <div className="profile-info">
            <div className="info-item">
              <label>Username:</label>
              <span>{stats?.username || user.username}</span>
            </div>
            <div className="info-item">
              <label>Profile Status:</label>
              <span className="status-badge active">{stats?.profileStatus || 'Active'}</span>
            </div>
            <div className="info-item">
              <label>Email:</label>
              <span>{user.email || 'Not set'}</span>
            </div>
          </div>
        </div>

        {/* Training Stats */}
        <div className="card stats-card">
          <h3>📝 Training Status</h3>
          <div className="stat-item">
            <label>Training Rounds:</label>
            <span className="stat-value">{stats?.trainingRounds || 0}</span>
          </div>
          <div className="stat-item">
            <label>Required Rounds:</label>
            <span className="stat-value">10</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${((stats?.trainingRounds || 0) / 10) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Detection Stats */}
        <div className="card detection-card">
          <h3>🔍 Detection Statistics</h3>
          <div className="stat-item">
            <label>Total Detections:</label>
            <span className="stat-value">{stats?.totalDetections || 0}</span>
          </div>
          <div className="stat-item">
            <label>Normal Attempts:</label>
            <span className="stat-value normal">{stats?.normalAttempts || 0}</span>
          </div>
          <div className="stat-item">
            <label>Intrusions Detected:</label>
            <span className="stat-value intrusion">{stats?.intrusionDetected || 0}</span>
          </div>
        </div>

        {/* Feature Profile */}
        <div className="card features-card">
          <h3>⌨️ Your Typing Features</h3>
          <div className="feature-item">
            <label>Avg. Dwell Time:</label>
            <span>{(stats?.features?.avgDwellTime || 0.12).toFixed(3)}s</span>
          </div>
          <div className="feature-item">
            <label>Avg. Flight Time:</label>
            <span>{(stats?.features?.avgFlightTime || 0.08).toFixed(3)}s</span>
          </div>
          <div className="feature-item">
            <label>Typing Speed:</label>
            <span>{stats?.features?.typingSpeed || 75} WPM</span>
          </div>
          <div className="feature-item">
            <label>Layout:</label>
            <span>{stats?.features?.keyboardLayout || 'QWERTY'}</span>
          </div>
        </div>

        {/* Accuracy */}
        <div className="card accuracy-card">
          <h3>📈 System Accuracy</h3>
          <div className="accuracy-display">
            <div className="accuracy-number">
              {stats?.accuracy || 0}%
            </div>
            <p>Detection Accuracy</p>
          </div>
          <p className="accuracy-note">
            {stats?.accuracy === 0 
              ? 'Complete training and run tests to see accuracy'
              : `Accuracy based on ${stats?.totalDetections || 0} detections`
            }
          </p>
        </div>

        {/* Recent Activity */}
        <div className="card activity-card">
          <h3>📋 Recent Activity</h3>
          {stats?.recentActivity && stats.recentActivity.length > 0 ? (
            <ul className="activity-list">
              {stats.recentActivity.map((activity, idx) => (
                <li key={idx}>
                  <span className="activity-time">{activity.time}</span>
                  <span className="activity-desc">{activity.description}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="no-activity">No recent activity</p>
          )}
        </div>
      </div>

      {/* Info Section */}
      <div className="info-section">
        <h3>📚 How KeyGuard Works</h3>
        <div className="info-grid">
          <div className="info-box">
            <h4>🎯 Training Phase</h4>
            <p>
              You type a phrase 10 times to establish your unique typing pattern. 
              The system measures dwell times (key hold duration) and flight times 
              (gaps between keystrokes).
            </p>
          </div>
          <div className="info-box">
            <h4>🔍 Detection Phase</h4>
            <p>
              During login, your typing is compared against your training profile. 
              The One-Class SVM model detects if typing patterns match your profile 
              or indicate an unauthorized user.
            </p>
          </div>
          <div className="info-box">
            <h4>📊 Features Analyzed</h4>
            <p>
              System extracts 31 features per login attempt: 16 dwell times and 
              15 flight times. These unique patterns form your biometric signature.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
