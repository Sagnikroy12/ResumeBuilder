import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import Navbar from '../components/Navbar';
import { User, Briefcase, Code, GraduationCap, Award, Settings, Save, Wand2, Loader2, Plus, Trash2 } from 'lucide-react';

const ResumeBuilderPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [activeSection, setActiveSection] = useState('personal');

  const [formData, setFormData] = useState({
    personal: { name: '', email: '', phone: '', address: '', linkedin: '' },
    objective: '',
    experience: [],
    skills: '',
    projects: '',
    education: '',
    certifications: '',
    custom_sections: [],
    template: searchParams.get('template') || 'template1'
  });

  const handleInputChange = (section, field, value) => {
    if (field) {
      setFormData(prev => ({
        ...prev,
        [section]: { ...prev[section], [field]: value }
      }));
    } else {
      setFormData(prev => ({ ...prev, [section]: value }));
    }
  };

  const addExperience = () => {
    setFormData(prev => ({
      ...prev,
      experience: [...prev.experience, { title: '', duration: '', points: '' }]
    }));
  };

  const removeExperience = (index) => {
    setFormData(prev => ({
      ...prev,
      experience: prev.experience.filter((_, i) => i !== index)
    }));
  };

  const updateExperience = (index, field, value) => {
    const newExp = [...formData.experience];
    newExp[index][field] = value;
    setFormData(prev => ({ ...prev, experience: newExp }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/api/resumes', formData);
      alert('Resume saved successfully!');
      navigate('/');
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to save resume');
    } finally {
      setLoading(false);
    }
  };

  const getAiSuggestion = async (section, context) => {
    setAiLoading(true);
    try {
      const response = await api.post('/api/suggest', { section, context });
      if (section === 'objective') {
        handleInputChange('objective', null, response.data.suggestion);
      } else {
        alert('Suggestion: ' + response.data.suggestion);
      }
    } catch (err) {
      alert('AI failed to provide a suggestion');
    } finally {
      setAiLoading(false);
    }
  };

  const sections = [
    { id: 'personal', label: 'Personal Information', icon: <User size={18} /> },
    { id: 'objective', label: 'Summary/Objective', icon: <Wand2 size={18} /> },
    { id: 'experience', label: 'Experience', icon: <Briefcase size={18} /> },
    { id: 'skills', label: 'Skills', icon: <Code size={18} /> },
    { id: 'education', label: 'Education', icon: <GraduationCap size={18} /> },
    { id: 'more', label: 'Projects & More', icon: <Award size={18} /> }
  ];

  return (
    <div className="builder-page">
      <Navbar />
      
      <div className="builder-container">
        <aside className="builder-sidebar glass">
          {sections.map(s => (
            <button 
              key={s.id}
              className={`section-btn ${activeSection === s.id ? 'active' : ''}`}
              onClick={() => setActiveSection(s.id)}
            >
              {s.icon}
              <span>{s.label}</span>
            </button>
          ))}
          <div className="sidebar-footer">
            <button onClick={handleSave} className="save-btn" disabled={loading}>
              {loading ? <Loader2 className="animate-spin" /> : <><Save size={18} /> Save Resume</>}
            </button>
          </div>
        </aside>

        <main className="builder-form-wrapper glass">
          <form id="resume-form" onSubmit={handleSave}>
            {activeSection === 'personal' && (
              <div className="form-section animate-slide-in">
                <h2>👤 Personal Details</h2>
                <div className="form-grid">
                  <div className="input-field">
                    <label>Full Name</label>
                    <input 
                      type="text" 
                      value={formData.personal.name} 
                      onChange={(e) => handleInputChange('personal', 'name', e.target.value)}
                      placeholder="John Doe"
                    />
                  </div>
                  <div className="input-field">
                    <label>Email</label>
                    <input 
                      type="email" 
                      value={formData.personal.email} 
                      onChange={(e) => handleInputChange('personal', 'email', e.target.value)}
                      placeholder="john@example.com"
                    />
                  </div>
                  <div className="input-field">
                    <label>Phone</label>
                    <input 
                      type="text" 
                      value={formData.personal.phone} 
                      onChange={(e) => handleInputChange('personal', 'phone', e.target.value)}
                      placeholder="+91 9876543210"
                    />
                  </div>
                  <div className="input-field">
                    <label>Address</label>
                    <input 
                      type="text" 
                      value={formData.personal.address} 
                      onChange={(e) => handleInputChange('personal', 'address', e.target.value)}
                      placeholder="City, Country"
                    />
                  </div>
                  <div className="input-field full">
                    <label>LinkedIn URL</label>
                    <input 
                      type="text" 
                      value={formData.personal.linkedin} 
                      onChange={(e) => handleInputChange('personal', 'linkedin', e.target.value)}
                      placeholder="linkedin.com/in/johndoe"
                    />
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'objective' && (
              <div className="form-section animate-slide-in">
                <div className="section-header">
                  <h2>🎯 Professional Summary</h2>
                  <button 
                    type="button" 
                    className="ai-btn"
                    onClick={() => getAiSuggestion('objective', formData.personal.name)}
                    disabled={aiLoading}
                  >
                    {aiLoading ? <Loader2 size={16} className="animate-spin" /> : <Wand2 size={16} />}
                    Magic Suggest
                  </button>
                </div>
                <textarea 
                  value={formData.objective}
                  onChange={(e) => handleInputChange('objective', null, e.target.value)}
                  placeholder="Tell us about your career goals and key achievements..."
                  rows={8}
                />
              </div>
            )}

            {activeSection === 'experience' && (
              <div className="form-section animate-slide-in">
                <div className="section-header">
                  <h2>💼 Work Experience</h2>
                  <button type="button" onClick={addExperience} className="add-btn">
                    <Plus size={16} /> Add Position
                  </button>
                </div>
                <div className="experience-list">
                  {formData.experience.map((exp, index) => (
                    <div key={index} className="experience-item glass">
                      <button type="button" onClick={() => removeExperience(index)} className="remove-item-btn">
                        <Trash2 size={16} />
                      </button>
                      <div className="form-grid">
                        <div className="input-field">
                          <label>Job Title</label>
                          <input 
                            type="text" 
                            value={exp.title}
                            onChange={(e) => updateExperience(index, 'title', e.target.value)}
                            placeholder="Software Engineer"
                          />
                        </div>
                        <div className="input-field">
                          <label>Duration</label>
                          <input 
                            type="text" 
                            value={exp.duration}
                            onChange={(e) => updateExperience(index, 'duration', e.target.value)}
                            placeholder="Jan 2020 - Present"
                          />
                        </div>
                        <div className="input-field full">
                          <label>Responsibilities (Use bullets or new lines)</label>
                          <textarea 
                            value={exp.points}
                            onChange={(e) => updateExperience(index, 'points', e.target.value)}
                            placeholder="- Built scalable microservices\n- Led team of 5"
                            rows={4}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeSection === 'skills' && (
              <div className="form-section animate-slide-in">
                <h2>🛠️ Skills</h2>
                <textarea 
                  value={formData.skills}
                  onChange={(e) => handleInputChange('skills', null, e.target.value)}
                  placeholder="Programming: React, Node.js\nDesign: Figma, Adobe XD"
                  rows={8}
                />
              </div>
            )}

            {activeSection === 'education' && (
              <div className="form-section animate-slide-in">
                <h2>🎓 Education</h2>
                <textarea 
                  value={formData.education}
                  onChange={(e) => handleInputChange('education', null, e.target.value)}
                  placeholder="Bachelor of Technology in CS, University of Excellence (2018-2022)"
                  rows={8}
                />
              </div>
            )}

            {activeSection === 'more' && (
              <div className="form-section animate-slide-in">
                <h2>📂 Projects & Certifications</h2>
                <div className="input-group">
                  <label>Projects</label>
                  <textarea 
                    value={formData.projects}
                    onChange={(e) => handleInputChange('projects', null, e.target.value)}
                    placeholder="- Portfolio Website\n- E-commerce App"
                    rows={4}
                  />
                </div>
                <div className="input-group mt-4">
                  <label>Certifications</label>
                  <textarea 
                    value={formData.certifications}
                    onChange={(e) => handleInputChange('certifications', null, e.target.value)}
                    placeholder="- AWS Certified Solutions Architect\n- Meta Front-End Developer"
                    rows={4}
                  />
                </div>
              </div>
            )}
          </form>
        </main>
      </div>
    </div>
  );
};

export default ResumeBuilderPage;
