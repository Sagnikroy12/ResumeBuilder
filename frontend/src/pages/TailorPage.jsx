import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import Navbar from '../components/Navbar';
import { Target, FileText, Wand2, Loader2, AlertCircle, CheckCircle } from 'lucide-react';

const TailorPage = () => {
  const [resumes, setResumes] = useState([]);
  const [selectedResume, setSelectedResume] = useState('');
  const [jd, setJd] = useState('');
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    try {
      const response = await api.get('/api/dashboard');
      setResumes(response.data.resumes);
    } catch (err) {
      setError('Failed to load resumes');
    } finally {
      setFetchLoading(false);
    }
  };

  const handleTailor = async () => {
    if (!selectedResume || !jd) return;
    setLoading(true);
    try {
      const response = await api.post('/api/tailor', {
        resume_id: selectedResume,
        job_description: jd
      });
      alert('Resume tailored successfully! Download starting...');
      // Logic to download or redirect
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Tailoring failed');
    } finally {
      setLoading(false);
    }
  };

  if (fetchLoading) return <div className="loading-screen">Preparing your tools...</div>;

  return (
    <div className="tailor-page">
      <Navbar />
      <div className="tailor-container">
        <header className="tailor-header">
          <div className="tailor-icon-premium">
            <Target size={32} />
          </div>
          <h1>Tailor to Job Description</h1>
          <p>Optimize your resume with AI to match specific job requirements and beat the ATS.</p>
        </header>

        <div className="tailor-grid">
          <div className="tailor-card glass">
            <h3>1. Select Base Resume</h3>
            <div className="resume-selector">
              {resumes.length === 0 ? (
                <p className="empty-msg">No resumes found. Create one first!</p>
              ) : (
                resumes.map(r => (
                  <label key={r.id} className={`resume-option ${selectedResume === r.id ? 'selected' : ''}`}>
                    <input 
                      type="radio" 
                      name="resume" 
                      value={r.id} 
                      onChange={(e) => setSelectedResume(e.target.value)}
                      hidden
                    />
                    <FileText size={20} />
                    <span>{r.title}</span>
                    {selectedResume === r.id && <CheckCircle size={16} className="check-icon" />}
                  </label>
                ))
              )}
            </div>
          </div>

          <div className="tailor-card glass">
            <h3>2. Paste Job Description</h3>
            <textarea 
              value={jd}
              onChange={(e) => setJd(e.target.value)}
              placeholder="Paste the job requirements, responsibilities, and qualifications here..."
              rows={12}
            />
            {error && <div className="error-msg"><AlertCircle size={16} /> {error}</div>}
            <button 
              onClick={handleTailor} 
              className="tailor-btn"
              disabled={loading || !selectedResume || !jd}
            >
              {loading ? <Loader2 className="animate-spin" /> : <><Wand2 size={18} /> Tailor Resume with AI</>}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TailorPage;
