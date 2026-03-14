import React, { useState } from 'react';
import api from '../services/api';
import Navbar from '../components/Navbar';
import { Check, Zap, Shield, Rocket, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const UpgradePage = () => {
  const [loading, setLoading] = useState(false);
  const { checkUser } = useAuth();
  const navigate = useNavigate();

  const handleUpgrade = async () => {
    setLoading(true);
    try {
      await api.post('/api/upgrade_pro');
      await checkUser();
      alert('Congratulations! You are now a Pro member.');
      navigate('/');
    } catch (err) {
      alert('Upgrade failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const features = [
    'Unlimited Resume Generation',
    'AI-Powered Resumes (100 daily)',
    '100 PDF Downloads per day',
    'Premium Templates Access',
    'Advanced Job Tailoring',
    'Priority Support'
  ];

  return (
    <div className="upgrade-page">
      <Navbar />
      <div className="upgrade-container">
        <header className="upgrade-header">
          <h1>Turbocharge Your Career</h1>
          <p>Choose the plan that fits your professional goals</p>
        </header>

        <div className="plans-grid">
          <div className="plan-card glass">
            <div className="plan-header">
              <h2>Free</h2>
              <div className="price">₹0<span>/forever</span></div>
            </div>
            <ul className="plan-features">
              <li><Check size={18} /> 10 Resumes / day</li>
              <li><Check size={18} /> 10 Downloads / day</li>
              <li><Check size={18} /> Basic Templates</li>
            </ul>
            <button className="plan-btn disabled" disabled>Current Plan</button>
          </div>

          <div className="plan-card glass premium">
            <div className="popular-tag">Most Popular</div>
            <div className="plan-header">
              <h2>Pro</h2>
              <div className="price">₹1,00,000<span>/one-time</span></div>
            </div>
            <ul className="plan-features">
              {features.map((f, i) => (
                <li key={i}><Zap size={18} className="zap-icon" /> {f}</li>
              ))}
            </ul>
            <button onClick={handleUpgrade} className="plan-btn primary" disabled={loading}>
              {loading ? <Loader2 className="animate-spin" /> : 'Upgrade to Pro'}
            </button>
          </div>
        </div>

        <section className="upgrade-footer">
          <div className="trust-item">
            <Shield size={24} />
            <p>Secure SSL Payment</p>
          </div>
          <div className="trust-item">
            <Rocket size={24} />
            <p>Instant Activation</p>
          </div>
        </section>
      </div>
    </div>
  );
};

export default UpgradePage;
