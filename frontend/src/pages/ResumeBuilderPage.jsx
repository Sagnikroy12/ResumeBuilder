import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate, useLocation } from 'react-router-dom';
import api from '../services/api';
import Navbar from '../components/Navbar';
import { User, Briefcase, Code, GraduationCap, Award, Settings, Save, Wand2, Loader2, Plus, Trash2, Layout } from 'lucide-react';

const ResumeBuilderPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [activeSection, setActiveSection] = useState('personal');
  const [usedAi, setUsedAi] = useState(location.state?.usedAi || false);

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

  // Pre-fill data if passed from parsing/tailoring
  useEffect(() => {
    if (location.state?.resumeData) {
      const rd = location.state.resumeData;
      setFormData(prev => ({
        ...prev,
        ...rd,
        // Ensure experience is always an array of objects
        experience: Array.isArray(rd.experience) 
          ? rd.experience.map(exp => typeof exp === 'object' ? exp : { title: exp, duration: '', points: '' })
          : [],
        template: prev.template // Keep the selected template
      }));
    }
  }, [location.state]);

  const [previewHtml, setPreviewHtml] = useState('');
  const [previewLoading, setPreviewLoading] = useState(false);
  const previewTimeoutRef = useRef(null);
  const previewContainerRef = useRef(null);
  const [previewScale, setPreviewScale] = useState(1);

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
    setFormData(prev => {
      const expArr = Array.isArray(prev.experience) ? prev.experience : [];
      return {
        ...prev,
        experience: [...expArr, { title: '', duration: '', points: '' }]
      };
    });
  };

  const removeExperience = (index) => {
    setFormData(prev => ({
      ...prev,
      experience: prev.experience.filter((_, i) => i !== index)
    }));
  };

  const updateExperience = (index, field, value) => {
    setFormData(prev => {
      const newExp = [...prev.experience];
      newExp[index] = { ...newExp[index], [field]: value };
      return { ...prev, experience: newExp };
    });
  };

  const addCustomSection = () => {
    setFormData(prev => ({
      ...prev,
      custom_sections: [...prev.custom_sections, { title: 'New Section', points: '' }]
    }));
  };

  const removeCustomSection = (index) => {
    setFormData(prev => ({
      ...prev,
      custom_sections: prev.custom_sections.filter((_, i) => i !== index)
    }));
  };

  const updateCustomSection = (index, field, value) => {
    const newSections = [...formData.custom_sections];
    newSections[index][field] = value;
    setFormData(prev => ({ ...prev, custom_sections: newSections }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/api/resumes', { ...formData, usedAi });
      alert('Resume saved successfully!');
      navigate('/');
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to save resume');
    } finally {
      setLoading(false);
    }
  };

  const getAiSuggestion = async (section, context, opts = {}) => {
    setAiLoading(true);
    setUsedAi(true);
    try {
      const response = await api.post('/api/suggest', { section, context });
      const suggestion = response.data.suggestion;

      if (section === 'objective') {
        handleInputChange('objective', null, suggestion);
      } else if (section === 'skills') {
        handleInputChange('skills', null, suggestion);
      } else if (section === 'projects') {
        handleInputChange('projects', null, suggestion);
      } else if (section === 'certifications') {
        handleInputChange('certifications', null, suggestion);
      } else if (section === 'experience' && typeof opts.index === 'number') {
        updateExperience(opts.index, 'points', suggestion);
      } else {
        alert('Suggestion: ' + suggestion);
      }
    } catch {
      alert('AI failed to provide a suggestion');
    } finally {
      setAiLoading(false);
    }
  };

  const fetchPreview = async (data) => {
    setPreviewLoading(true);
    try {
      const response = await api.post('/api/preview', data);
      setPreviewHtml(response.data.html);
    } catch {
      setPreviewHtml('<p style="color: red;">Unable to generate preview.</p>');
    } finally {
      setPreviewLoading(false);
    }
  };

  useEffect(() => {
    if (previewTimeoutRef.current) clearTimeout(previewTimeoutRef.current);
    previewTimeoutRef.current = setTimeout(() => {
      fetchPreview(formData);
    }, 400);

    return () => {
      if (previewTimeoutRef.current) clearTimeout(previewTimeoutRef.current);
    };
  }, [formData]);

  // A4 Preview Scaling Logic
  useEffect(() => {
    const calculateScale = () => {
      if (previewContainerRef.current) {
        const padding = 40;
        const containerWidth = previewContainerRef.current.clientWidth - padding;
        const a4WidthMm = 210;
        const mmToPx = 3.7795275591; // Standard conversion at 96 DPI
        const a4WidthPx = a4WidthMm * mmToPx;
        
        const scale = containerWidth / a4WidthPx;
        setPreviewScale(scale);
      }
    };

    calculateScale();
    // Add a small delay to ensure container is fully rendered
    const timer = setTimeout(calculateScale, 100);
    
    window.addEventListener('resize', calculateScale);
    return () => {
      window.removeEventListener('resize', calculateScale);
      clearTimeout(timer);
    };
  }, []);

  const sections = [
    { id: 'template', label: 'Template', icon: <Layout size={18} /> },
    { id: 'personal', label: 'Personal Information', icon: <User size={18} /> },
    { id: 'objective', label: 'Summary/Objective', icon: <Wand2 size={18} /> },
    { id: 'experience', label: 'Experience', icon: <Briefcase size={18} /> },
    { id: 'skills', label: 'Skills', icon: <Code size={18} /> },
    { id: 'education', label: 'Education', icon: <GraduationCap size={18} /> },
    { id: 'more', label: 'Projects & More', icon: <Award size={18} /> },
    { id: 'custom', label: 'Custom Sections', icon: <Plus size={18} /> }
  ];

  const isAiMode = searchParams.get('ai') === 'true';

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
            {usedAi && <p className="ai-notice">✨ AI Enhanced Pricing Applies</p>}
          </div>
        </aside>

        <main className="builder-main glass">
          <form id="resume-form" onSubmit={handleSave}>
            {activeSection === 'template' && (
              <div className="form-section animate-slide-in">
                <div className="section-header">
                  <h2>🎨 Resume Template</h2>
                </div>
                <div className="input-field">
                  <label>Select Your Style</label>
                  <div className="template-grid">
                    <select
                      className="template-select"
                      value={formData.template}
                      onChange={(e) => handleInputChange('template', null, e.target.value)}
                    >
                      <option value="template1">Classic (Elegant & Clean)</option>
                      <option value="template2">Modern (Creative & Fresh)</option>
                      <option value="template3">Professional (Executive & Detailed)</option>
                    </select>
                  </div>
                  <p className="hint-text">Choose a template that best fits your industry.</p>
                </div>
              </div>
            )}

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
                  {isAiMode && (
                    <button 
                      type="button" 
                      className="ai-btn"
                      onClick={() => getAiSuggestion('objective', formData.personal.name)}
                      disabled={aiLoading}
                    >
                      {aiLoading ? <Loader2 size={16} className="animate-spin" /> : <Wand2 size={16} />}
                      Magic Suggest
                    </button>
                  )}
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
                  <div className="section-header-actions">
                    <button
                      type="button"
                      className="ai-btn"
                      disabled={aiLoading || !Array.isArray(formData.experience) || formData.experience.length === 0}
                      onClick={() => {
                        const lastIndex = formData.experience.length - 1;
                        const lastExp = formData.experience[lastIndex] || {};
                        const context = `${lastExp.title || ''} ${lastExp.duration || ''}`.trim();
                        getAiSuggestion('experience', context, { index: lastIndex });
                      }}
                    >
                      {aiLoading ? <Loader2 size={16} className="animate-spin" /> : <Wand2 size={16} />}
                      Suggest
                    </button>
                    <button type="button" onClick={addExperience} className="add-btn">
                      <Plus size={16} /> Add Position
                    </button>
                  </div>
                </div>
                <div className="experience-list">
                  {Array.isArray(formData.experience) && formData.experience.map((exp, index) => (
                    <div key={index} className="experience-item glass">
                      <div className="experience-item-actions">
                        <button type="button" onClick={() => removeExperience(index)} className="remove-item-btn">
                          <Trash2 size={16} />
                        </button>
                        <button
                          type="button"
                          className="ai-btn mini"
                          onClick={() => {
                            const context = `${exp.title || ''} ${exp.duration || ''}`.trim();
                            getAiSuggestion('experience', context, { index });
                          }}
                          disabled={aiLoading}
                          title="Suggest responsibilities"
                        >
                          <Wand2 size={14} />
                        </button>
                      </div>
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
                <div className="section-header">
                  <h2>🛠️ Skills</h2>
                  <button
                    type="button"
                    className="ai-btn"
                    onClick={() => getAiSuggestion('skills', `${formData.skills || formData.personal.name}`)}
                    disabled={aiLoading}
                  >
                    {aiLoading ? <Loader2 size={16} className="animate-spin" /> : <Wand2 size={16} />}
                    Suggest
                  </button>
                </div>
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
                <div className="section-header">
                  <h2>📂 Projects & Certifications</h2>
                  <button
                    type="button"
                    className="ai-btn"
                    onClick={() => getAiSuggestion('projects', `${formData.projects || formData.personal.name}`)}
                    disabled={aiLoading}
                  >
                    {aiLoading ? <Loader2 size={16} className="animate-spin" /> : <Wand2 size={16} />}
                    Suggest
                  </button>
                </div>
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

            {activeSection === 'custom' && (
              <div className="form-section animate-slide-in">
                <div className="section-header">
                  <h2>➕ Custom Sections</h2>
                  <button type="button" onClick={addCustomSection} className="add-btn">
                    <Plus size={16} /> Add Section
                  </button>
                </div>
                <div className="custom-sections-list">
                  {formData.custom_sections.map((section, index) => (
                    <div key={index} className="custom-section-item glass">
                      <div className="custom-section-header">
                        <input 
                          type="text"
                          className="custom-section-title-input"
                          value={section.title}
                          onChange={(e) => updateCustomSection(index, 'title', e.target.value)}
                          placeholder="Section Title (e.g. Languages)"
                        />
                        <button type="button" onClick={() => removeCustomSection(index)} className="remove-item-btn">
                          <Trash2 size={16} />
                        </button>
                      </div>
                      <textarea 
                        value={section.points}
                        onChange={(e) => updateCustomSection(index, 'points', e.target.value)}
                        placeholder="Detail your information here..."
                        rows={4}
                      />
                    </div>
                  ))}
                  {formData.custom_sections.length === 0 && (
                    <p className="empty-notice">No custom sections added. Click 'Add Section' to add areas like Languages, Awards, or Hobbies.</p>
                  )}
                </div>
              </div>
            )}
          </form>
        </main>

        <aside className="builder-preview glass">
          <div className="preview-header">
            <h2>Live Preview</h2>
            {previewLoading && <span className="preview-loading">Updating...</span>}
          </div>
          <div className="preview-content" ref={previewContainerRef}>
            {previewHtml ? (
              <div 
                className="preview-scaler-wrapper" 
                style={{ 
                  height: `calc(${297 * previewScale}mm + 100px)` /* Extra space for overflow */
                }}
              >
                <div 
                  className="preview-scaler" 
                  style={{ 
                    transform: `scale(${previewScale})`,
                    height: 'auto',
                    minHeight: '297mm'
                  }}
                >
                  <iframe
                    title="Resume Preview"
                    srcDoc={previewHtml}
                    sandbox="allow-same-origin"
                    className="preview-iframe"
                    style={{ height: '2000px' }} /* Large enough height to show overflow content */
                    onLoad={(e) => {
                      // Try to adjust height based on content
                      try {
                        const contentHeight = e.target.contentWindow.document.body.scrollHeight;
                        e.target.style.height = Math.max(contentHeight, 1123) + 'px'; // 1123px is approx 297mm
                      } catch (err) {
                        e.target.style.height = '1500px'; 
                      }
                    }}
                  />
                  <div className="page-break-label">A4 PAGE 1 END</div>
                </div>
              </div>
            ) : (
              <div className="preview-placeholder">
                <p>Start typing to see a live preview of your resume.</p>
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
};

export default ResumeBuilderPage;
