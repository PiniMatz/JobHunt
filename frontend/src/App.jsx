import React, { useState, useEffect } from 'react';
import JobCard from './components/JobCard';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard', 'cv', 'settings'
  const [jobs, setJobs] = useState([]);
  const [settings, setSettings] = useState({
    cv_markdown: '',
    api_key: '',
    locations: ['Netanya'],
    threshold: 70,
    must_have_keywords: ['Product Manager', 'Product Owner', 'PM'],
    exclusion_keywords: ['Junior', 'Intern', 'Student']
  });

  const [loadingJobs, setLoadingJobs] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [scanStatus, setScanStatus] = useState('');
  const [uploadingCV, setUploadingCV] = useState(false);
  const [cvSuccessMessage, setCvSuccessMessage] = useState('');
  
  // Dashboard view sub-tabs
  const [dashboardView, setDashboardView] = useState('matched'); // 'matched', 'saved', 'applied', 'all'
  // Local threshold slider state
  const [localThreshold, setLocalThreshold] = useState(70);

  // Settings form states
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [locationsInput, setLocationsInput] = useState('');
  const [mustHaveInput, setMustHaveInput] = useState('');
  const [exclusionInput, setExclusionInput] = useState('');
  const [settingsSuccessMessage, setSettingsSuccessMessage] = useState('');

  // Fetch initial data
  useEffect(() => {
    fetchSettings();
    fetchJobs();
  }, []);

  const fetchSettings = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/settings');
      if (res.ok) {
        const data = await res.json();
        setSettings(data);
        setLocalThreshold(data.threshold);
        setApiKeyInput(data.api_key || '');
        setLocationsInput(data.locations.join(', '));
        setMustHaveInput(data.must_have_keywords ? data.must_have_keywords.join(', ') : 'Product Manager, Product Owner, PM');
        setExclusionInput(data.exclusion_keywords ? data.exclusion_keywords.join(', ') : 'Junior, Intern, Student');
      }
    } catch (err) {
      console.error('Error fetching settings:', err);
    }
  };

  const fetchJobs = async () => {
    setLoadingJobs(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/jobs');
      if (res.ok) {
        const data = await res.json();
        setJobs(data);
      }
    } catch (err) {
      console.error('Error fetching jobs:', err);
    } finally {
      setLoadingJobs(false);
    }
  };

  const handleScan = async () => {
    setScanning(true);
    setScanStatus('Scanning job listings in target areas...');
    try {
      const res = await fetch('http://127.0.0.1:8000/api/jobs/scan', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setScanStatus(`Scan complete! Found ${data.jobs_scanned} listings.`);
        fetchJobs();
      } else {
        const errData = await res.json();
        setScanStatus(`Scan failed: ${errData.detail || 'Unknown error'}`);
      }
    } catch (err) {
      setScanStatus(`Scan failed: ${err.message}`);
    } finally {
      setScanning(false);
      setTimeout(() => setScanStatus(''), 4000);
    }
  };

  const handleStatusChange = async (jobId, newStatus) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/jobs/${jobId}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      if (res.ok) {
        // Update local jobs list
        setJobs(prevJobs => prevJobs.map(job => 
          job.id === jobId ? { ...job, status: newStatus } : job
        ));
      }
    } catch (err) {
      console.error('Error updating status:', err);
    }
  };

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setSettingsSuccessMessage('');
    const locationsArray = locationsInput.split(',').map(s => s.trim()).filter(Boolean);
    const mustHaveArray = mustHaveInput.split(',').map(s => s.trim()).filter(Boolean);
    const exclusionArray = exclusionInput.split(',').map(s => s.trim()).filter(Boolean);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: apiKeyInput,
          locations: locationsArray,
          threshold: localThreshold,
          must_have_keywords: mustHaveArray,
          exclusion_keywords: exclusionArray
        })
      });
      if (res.ok) {
        const data = await res.json();
        setSettings(data.settings);
        setSettingsSuccessMessage('Settings updated successfully!');
        setTimeout(() => setSettingsSuccessMessage(''), 3000);
        // Refresh jobs (scores might recalculate or locations change)
        fetchJobs();
      }
    } catch (err) {
      console.error('Error saving settings:', err);
    }
  };

  const handleCVUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadingCV(true);
    setCvSuccessMessage('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/cv/upload', {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        setSettings(prev => ({ ...prev, cv_markdown: data.cv_markdown }));
        setCvSuccessMessage('CV uploaded and formatted successfully!');
        fetchJobs(); // Recalculate match scores since CV changed
      } else {
        const err = await res.json();
        alert(`Upload failed: ${err.detail || 'Unknown error'}`);
      }
    } catch (err) {
      alert(`Upload failed: ${err.message}`);
    } finally {
      setUploadingCV(false);
    }
  };

  // Filtering jobs based on tab and threshold
  const filteredJobs = jobs.filter(job => {
    // Exclude dismissed jobs from most views
    if (job.status === 'dismissed' && dashboardView !== 'all') return false;

    if (dashboardView === 'matched') {
      const score = job.match ? job.match.overall_score : 0;
      return job.status !== 'applied' && score >= localThreshold;
    }
    if (dashboardView === 'saved') {
      return job.status === 'starred';
    }
    if (dashboardView === 'applied') {
      return job.status === 'applied';
    }
    return true; // 'all' view
  });

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      
      {/* Sidebar Navigation */}
      <aside style={{
        width: '260px',
        backgroundColor: 'var(--bg-secondary)',
        borderRight: '1px solid var(--glass-border)',
        padding: '2rem 1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '2rem'
      }}>
        <div>
          <h2 style={{ 
            fontSize: '1.5rem', 
            fontWeight: '800', 
            background: 'linear-gradient(135deg, var(--accent-purple), var(--accent-blue))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '0.25rem'
          }}>
            JobHunt
          </h2>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Smart Career Agent v1.0</p>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
          <button 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            style={{
              textAlign: 'left',
              padding: '0.75rem 1rem',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeTab === 'dashboard' ? 'var(--bg-tertiary)' : 'transparent',
              color: activeTab === 'dashboard' ? 'var(--accent-purple)' : 'var(--text-secondary)',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all var(--transition-fast)'
            }}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Dashboard
          </button>
          
          <button 
            className={`nav-item ${activeTab === 'cv' ? 'active' : ''}`}
            style={{
              textAlign: 'left',
              padding: '0.75rem 1rem',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeTab === 'cv' ? 'var(--bg-tertiary)' : 'transparent',
              color: activeTab === 'cv' ? 'var(--accent-purple)' : 'var(--text-secondary)',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all var(--transition-fast)'
            }}
            onClick={() => setActiveTab('cv')}
          >
            📄 My CV
          </button>

          <button 
            className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            style={{
              textAlign: 'left',
              padding: '0.75rem 1rem',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeTab === 'settings' ? 'var(--bg-tertiary)' : 'transparent',
              color: activeTab === 'settings' ? 'var(--accent-purple)' : 'var(--text-secondary)',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all var(--transition-fast)'
            }}
            onClick={() => setActiveTab('settings')}
          >
            ⚙️ Settings
          </button>
        </nav>

        <div style={{ borderTop: '1px solid var(--glass-border)', paddingTop: '1rem' }}>
          <button 
            onClick={handleScan}
            disabled={scanning}
            style={{
              width: '100%',
              padding: '0.75rem',
              borderRadius: '8px',
              border: 'none',
              background: 'linear-gradient(135deg, var(--accent-purple), var(--accent-blue))',
              color: 'white',
              fontWeight: 'bold',
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(139, 92, 246, 0.25)',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            {scanning ? 'Scanning...' : '🚀 Scan for Jobs'}
          </button>
          {scanStatus && (
            <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '0.5rem', textAlign: 'center' }}>
              {scanStatus}
            </p>
          )}
        </div>
      </aside>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '2.5rem', overflowY: 'auto', maxHeight: '100vh' }}>
        
        {activeTab === 'dashboard' && (
          <div className="animate-fade-in">
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <div>
                <h1 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>Opportunity Hub</h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                  Smart career agent filtering PM listings in {settings.locations.join(', ')}.
                </p>
              </div>

              {/* Threshold Slider control */}
              <div className="glass-panel" style={{ padding: '0.75rem 1.25rem', display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block' }}>Match Filter Threshold</span>
                  <strong style={{ color: 'var(--accent-purple)', fontSize: '1.15rem' }}>{localThreshold}% +</strong>
                </div>
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  value={localThreshold} 
                  onChange={(e) => setLocalThreshold(parseInt(e.target.value))}
                  style={{
                    cursor: 'pointer',
                    width: '120px',
                    accentColor: 'var(--accent-purple)'
                  }}
                />
              </div>
            </header>

            {/* Dashboard Sub Tabs */}
            <div style={{ display: 'flex', borderBottom: '1px solid var(--glass-border)', gap: '1.5rem', marginBottom: '1.5rem' }}>
              <button 
                style={{
                  padding: '0.5rem 0.25rem',
                  border: 'none',
                  borderBottom: dashboardView === 'matched' ? '2px solid var(--accent-purple)' : 'none',
                  backgroundColor: 'transparent',
                  color: dashboardView === 'matched' ? 'var(--text-primary)' : 'var(--text-secondary)',
                  fontWeight: '600',
                  cursor: 'pointer',
                  fontSize: '0.9rem'
                }}
                onClick={() => setDashboardView('matched')}
              >
                ✨ Ideal Matches ({jobs.filter(j => j.status !== 'applied' && (j.match ? j.match.overall_score : 0) >= localThreshold).length})
              </button>
              
              <button 
                style={{
                  padding: '0.5rem 0.25rem',
                  border: 'none',
                  borderBottom: dashboardView === 'saved' ? '2px solid var(--accent-purple)' : 'none',
                  backgroundColor: 'transparent',
                  color: dashboardView === 'saved' ? 'var(--text-primary)' : 'var(--text-secondary)',
                  fontWeight: '600',
                  cursor: 'pointer',
                  fontSize: '0.9rem'
                }}
                onClick={() => setDashboardView('saved')}
              >
                ⭐ Saved ({jobs.filter(j => j.status === 'starred').length})
              </button>

              <button 
                style={{
                  padding: '0.5rem 0.25rem',
                  border: 'none',
                  borderBottom: dashboardView === 'applied' ? '2px solid var(--accent-purple)' : 'none',
                  backgroundColor: 'transparent',
                  color: dashboardView === 'applied' ? 'var(--text-primary)' : 'var(--text-secondary)',
                  fontWeight: '600',
                  cursor: 'pointer',
                  fontSize: '0.9rem'
                }}
                onClick={() => setDashboardView('applied')}
              >
                ✔️ Applied ({jobs.filter(j => j.status === 'applied').length})
              </button>

              <button 
                style={{
                  padding: '0.5rem 0.25rem',
                  border: 'none',
                  borderBottom: dashboardView === 'all' ? '2px solid var(--accent-purple)' : 'none',
                  backgroundColor: 'transparent',
                  color: dashboardView === 'all' ? 'var(--text-primary)' : 'var(--text-secondary)',
                  fontWeight: '600',
                  cursor: 'pointer',
                  fontSize: '0.9rem'
                }}
                onClick={() => setDashboardView('all')}
              >
                📂 All Scraped ({jobs.length})
              </button>
            </div>

            {/* Listings Grid */}
            {loadingJobs ? (
              <div style={{ color: 'var(--text-secondary)', padding: '2rem 0' }}>Loading job database...</div>
            ) : filteredJobs.length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1rem' }}>
                {filteredJobs.map(job => (
                  <JobCard 
                    key={job.id} 
                    job={job} 
                    onStatusChange={handleStatusChange} 
                  />
                ))}
              </div>
            ) : (
              <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                <p style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>No jobs found in this tab.</p>
                <p style={{ fontSize: '0.85rem' }}>
                  {dashboardView === 'matched' 
                    ? `Try lowering the threshold slider (currently ${localThreshold}%) or click 'Scan for Jobs' to scrape.`
                    : "Star items, apply to them, or scan for new listings to populate this view."}
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'cv' && (
          <div className="animate-fade-in" style={{ maxWidth: '800px' }}>
            <header style={{ marginBottom: '2rem' }}>
              <h1 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>My CV / Resume</h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                Ingest your CV PDF and manage the parsed Markdown text used by the LLM matching engine.
              </p>
            </header>

            {/* Upload PDF Section */}
            <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>Upload PDF CV</h3>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                <input 
                  type="file" 
                  accept=".pdf" 
                  onChange={handleCVUpload}
                  disabled={uploadingCV}
                  style={{
                    backgroundColor: 'rgba(255,255,255,0.03)',
                    padding: '0.75rem',
                    borderRadius: '8px',
                    border: '1px dashed var(--glass-border)',
                    cursor: 'pointer'
                  }}
                />
                {uploadingCV && <span style={{ color: 'var(--accent-purple)' }}>Processing and converting PDF text...</span>}
                {cvSuccessMessage && <span style={{ color: 'var(--score-high)' }}>{cvSuccessMessage}</span>}
              </div>
            </div>

            {/* Parsed CV Markdown */}
            <div className="glass-panel" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.1rem' }}>Parsed Resume Text (Markdown)</h3>
                <button 
                  style={{
                    padding: '0.4rem 0.8rem',
                    backgroundColor: 'var(--bg-tertiary)',
                    border: '1px solid var(--glass-border)',
                    borderRadius: '6px',
                    color: 'var(--text-primary)',
                    cursor: 'pointer',
                    fontSize: '0.8rem'
                  }}
                  onClick={async () => {
                    const newText = prompt("Edit CV Markdown:", settings.cv_markdown);
                    if (newText !== null) {
                      const res = await fetch('http://127.0.0.1:8000/api/settings', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ cv_markdown: newText })
                      });
                      if (res.ok) {
                        setSettings(prev => ({ ...prev, cv_markdown: newText }));
                        fetchJobs();
                      }
                    }
                  }}
                >
                  ✏️ Edit Manually
                </button>
              </div>
              
              {settings.cv_markdown ? (
                <div style={{
                  backgroundColor: 'rgba(0,0,0,0.2)',
                  padding: '1rem',
                  borderRadius: '6px',
                  fontFamily: 'monospace',
                  fontSize: '0.8rem',
                  whiteSpace: 'pre-wrap',
                  maxHeight: '400px',
                  overflowY: 'auto',
                  border: '1px solid rgba(255,255,255,0.05)',
                  color: 'var(--text-secondary)'
                }}>
                  {settings.cv_markdown}
                </div>
              ) : (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                  No CV data uploaded yet. Please upload a PDF above.
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="animate-fade-in" style={{ maxWidth: '600px' }}>
            <header style={{ marginBottom: '2rem' }}>
              <h1 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>Settings</h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                Configure Gemini API, default search locations, and threshold parameters.
              </p>
            </header>

            <form onSubmit={handleSaveSettings} className="glass-panel" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                  Gemini API Key
                </label>
                <input 
                  type="password" 
                  value={apiKeyInput}
                  onChange={(e) => setApiKeyInput(e.target.value)}
                  placeholder="Enter your GEMINI_API_KEY"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    borderRadius: '8px',
                    border: '1px solid var(--glass-border)',
                    backgroundColor: 'var(--bg-tertiary)',
                    color: 'white',
                    fontSize: '0.9rem'
                  }}
                />
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem', display: 'block' }}>
                  Leave empty to fallback to GEMINI_API_KEY environment variable. Enter "MOCK_API_KEY" to test matches offline.
                </span>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                  Target Locations (comma-separated)
                </label>
                <input 
                  type="text" 
                  value={locationsInput}
                  onChange={(e) => setLocationsInput(e.target.value)}
                  placeholder="Netanya, Tel Aviv, Herzliya"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    borderRadius: '8px',
                    border: '1px solid var(--glass-border)',
                    backgroundColor: 'var(--bg-tertiary)',
                    color: 'white',
                    fontSize: '0.9rem'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                  Must-Have Pre-Screening Keywords (comma-separated)
                </label>
                <input 
                  type="text" 
                  value={mustHaveInput}
                  onChange={(e) => setMustHaveInput(e.target.value)}
                  placeholder="Product Manager, Product Owner, PM"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    borderRadius: '8px',
                    border: '1px solid var(--glass-border)',
                    backgroundColor: 'var(--bg-tertiary)',
                    color: 'white',
                    fontSize: '0.9rem'
                  }}
                />
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem', display: 'block' }}>
                  At least one of these keywords must exist in the title/description to trigger an LLM match (saves API cost).
                </span>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                  Exclusion Title Keywords (comma-separated)
                </label>
                <input 
                  type="text" 
                  value={exclusionInput}
                  onChange={(e) => setExclusionInput(e.target.value)}
                  placeholder="Junior, Intern, Student"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    borderRadius: '8px',
                    border: '1px solid var(--glass-border)',
                    backgroundColor: 'var(--bg-tertiary)',
                    color: 'white',
                    fontSize: '0.9rem'
                  }}
                />
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem', display: 'block' }}>
                  Jobs containing these words in their title will be immediately filtered out (saves API cost).
                </span>
              </div>

              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                    Match Threshold ({localThreshold}%)
                  </label>
                  <input 
                    type="range" 
                    min="0" 
                    max="100" 
                    value={localThreshold} 
                    onChange={(e) => setLocalThreshold(parseInt(e.target.value))}
                    style={{
                      width: '100%',
                      cursor: 'pointer',
                      accentColor: 'var(--accent-purple)'
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '1rem' }}>
                <button 
                  type="submit"
                  style={{
                    padding: '0.75rem 1.5rem',
                    borderRadius: '8px',
                    border: 'none',
                    backgroundColor: 'var(--accent-purple)',
                    color: 'white',
                    fontWeight: 'bold',
                    cursor: 'pointer',
                    fontSize: '0.9rem'
                  }}
                >
                  Save Settings
                </button>
                {settingsSuccessMessage && <span style={{ color: 'var(--score-high)', fontSize: '0.85rem' }}>{settingsSuccessMessage}</span>}
              </div>
            </form>
          </div>
        )}
        
      </main>
    </div>
  );
}

export default App;
