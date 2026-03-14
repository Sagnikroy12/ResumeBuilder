import React, { useState, useEffect } from 'react';
import api from '../services/api';
import Navbar from '../components/Navbar';
import { FileText, Download, Trash2, Plus, Sparkles, Wand2, Upload, Target } from 'lucide-react';
import { Link } from 'react-router-dom';

const DashboardPage = () => {
  const [resumes, setResumes] = useState([]);
  const [templates, setTemplates] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/api/dashboard');
      setResumes(response.data.resumes);
      setTemplates(response.data.templates);
    } catch (err) {
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this resume?')) return;
    try {
      await api.delete(`/api/delete/${id}`);
      setResumes(resumes.filter(r => r.id !== id));
    } catch (err) {
      alert('Failed to delete resume');
    }
  };

  const handleDownload = async (id, title) => {
    try {
      const response = await api.get(`/api/download/${id}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${title}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      if (err.response?.status === 402 || err.response?.status === 403) {
        alert(err.response.data.message);
        // Handle redirection if needed
      } else {
        alert('Download failed');
      }
    }
  };

  if (loading) return <div className="loading-screen">Loading your workspace...</div>;

  return (
    <div className="dashboard-page">
      <Navbar />
      
      <main className="dashboard-content">
        <header className="content-header">
          <h1>My Workspace</h1>
          <p>Create and manage your professional resumes</p>
        </header>

        <section className="quick-actions">
          <h3>✨ Quick Create</h3>
          <div className="actions-grid">
            <Link to="/create" className="action-card">
              <div className="action-icon manual"><Plus /></div>
              <h4>Manual</h4>
              <p>Build from scratch</p>
            </Link>
            <Link to="/create?ai=true" className="action-card">
              <div className="action-icon ai"><Wand2 /></div>
              <h4>AI Assisted</h4>
              <p>Smart suggestions</p>
            </Link>
            <Link to="/upload" className="action-card">
              <div className="action-icon upload"><Upload /></div>
              <h4>Upload & Parse</h4>
              <p>Magic auto-fill</p>
            </Link>
            <Link to="/tailor" className="action-card">
              <div className="action-icon tailor"><Target /></div>
              <h4>Tailor to JD</h4>
              <p>Optimize for jobs</p>
            </Link>
          </div>
        </section>

        <section className="templates-section">
          <h3>📋 Choose a Template</h3>
          <div className="templates-scroll">
            {Object.entries(templates).map(([id, template]) => (
              <div key={id} className="template-card glass">
                <div className="template-preview">
                  <div className="template-placeholder">
                    <FileText size={48} />
                  </div>
                  <div className="template-overlay">
                    <Link to={`/create?template=${id}`} className="use-template-btn">Use This</Link>
                  </div>
                </div>
                <div className="template-info">
                  <h4>{template.name}</h4>
                  <p>{template.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="resumes-section">
          <h3>📂 My Saved Resumes</h3>
          {resumes.length === 0 ? (
            <div className="empty-state glass">
              <FileText size={48} className="empty-icon" />
              <p>You haven't created any resumes yet.</p>
              <Link to="/create" className="btn-primary">Create Your First Resume</Link>
            </div>
          ) : (
            <div className="resumes-grid">
              {resumes.map(resume => (
                <div key={resume.id} className="resume-card glass">
                  <div className="resume-card-header">
                    <h3>{resume.title}</h3>
                    <button onClick={() => handleDelete(resume.id)} className="delete-btn">
                      <Trash2 size={18} />
                    </button>
                  </div>
                  <div className="resume-card-body">
                    <p>Created: {new Date(resume.created_at).toLocaleDateString()}</p>
                    <div className="resume-actions">
                      <button 
                        onClick={() => handleDownload(resume.id, resume.title)}
                        className="download-btn"
                      >
                        <Download size={18} />
                        <span>Download PDF</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

export default DashboardPage;
