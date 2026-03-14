import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import Navbar from '../components/Navbar';
import { CreditCard, Lock, ShieldCheck, Loader2 } from 'lucide-react';

const PaymentPage = () => {
  const { resumeId } = useParams();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handlePayment = async () => {
    setLoading(true);
    try {
      const response = await api.post(`/api/verify_payment/${resumeId}`, {}, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'resume.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      alert('Payment successful! Your download has started.');
      navigate('/');
    } catch (err) {
      alert('Payment failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="payment-page">
      <Navbar />
      <div className="payment-container">
        <div className="payment-card glass">
          <header className="payment-header">
            <div className="payment-icon">
              <CreditCard size={32} />
            </div>
            <h1>Secure Checkout</h1>
            <p>Complete payment to download your premium resume</p>
          </header>

          <div className="order-summary">
            <div className="summary-row">
              <span>Premium Resume Download</span>
              <span className="price">₹50.00</span>
            </div>
            <div className="summary-total">
              <span>Total Amount</span>
              <span>₹50.00</span>
            </div>
          </div>

          <div className="mock-payment-form">
            <div className="payment-notice">
              <Lock size={16} />
              <span>This is a mock payment gateway for demonstration.</span>
            </div>
            
            <button onClick={handlePayment} className="pay-btn" disabled={loading}>
              {loading ? <Loader2 className="animate-spin" /> : 'Pay ₹50 & Download'}
            </button>
          </div>

          <footer className="payment-footer">
            <ShieldCheck size={16} />
            <span>Secure 256-bit SSL Encrypted Payment</span>
          </footer>
        </div>
      </div>
    </div>
  );
};

export default PaymentPage;
