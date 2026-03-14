import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import Navbar from '../components/Navbar';
import { Upload, FileType, CheckCircle2, Loader2, AlertCircle } from 'lucide-react';

const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError('');
    } else {
      setFile(null);
      setError('Please upload a valid PDF file');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      // Assuming backup or data is returned to pre-fill builder
      alert('Resume parsed successfully! Redirecting to editor...');
      navigate('/create?ai=true', { 
        state: { 
          resumeData: response.data.extracted_data,
          usedAi: true 
        } 
      });
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-page">
      <Navbar />
      <div className="upload-container">
        <div className="upload-card glass">
          <header className="upload-header">
            <div className="upload-icon-wrapper">
              <Upload size={32} />
            </div>
            <h1>Magic Parse</h1>
            <p>Upload your existing PDF resume and we'll extract the data for you.</p>
          </header>

          <div className={`dropzone ${file ? 'has-file' : ''}`} onClick={() => document.getElementById('file-input').click()}>
            <input 
              type="file" 
              id="file-input" 
              hidden 
              accept=".pdf" 
              onChange={handleFileChange}
            />
            {file ? (
              <div className="file-info">
                <FileType size={48} className="file-icon" />
                <span className="file-name">{file.name}</span>
                <span className="file-size">{(file.size / 1024).toFixed(1)} KB</span>
              </div>
            ) : (
              <div className="prompt">
                <Upload size={48} className="prompt-icon" />
                <span>Click or drag and drop your PDF here</span>
              </div>
            )}
          </div>

          {error && (
            <div className="error-notice">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <button 
            onClick={handleUpload} 
            className="upload-btn-primary" 
            disabled={!file || loading}
          >
            {loading ? <Loader2 className="animate-spin" /> : 'Start Parsing Resume'}
          </button>

          <div className="upload-features">
            <div className="feature">
              <CheckCircle2 size={16} />
              <span>Extracts experience & skills</span>
            </div>
            <div className="feature">
              <CheckCircle2 size={16} />
              <span>Saves manual entry time</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
