import React, { useState } from 'react';

const JobCard = ({ job, onStatusChange, onJobUpdate }) => {
  const [expanded, setExpanded] = useState(false);
  const [suggestions, setSuggestions] = useState(null);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [errorSuggestions, setErrorSuggestions] = useState('');
  
  const [runningMatch, setRunningMatch] = useState(false);
  const [matchError, setMatchError] = useState('');

  const match = job.match;
  const overallScore = match ? match.overall_score : null;

  // Colors based on score
  const getScoreColor = (score) => {
    if (score >= 75) return 'var(--score-high)';
    if (score >= 60) return 'var(--score-medium)';
    return 'var(--score-low)';
  };

  const getJobSource = (url) => {
    if (!url) return 'Direct Source';
    const lowercaseUrl = url.toLowerCase();
    if (lowercaseUrl.includes('drushim.co.il')) return 'Drushim';
    if (lowercaseUrl.includes('jobmaster.co.il')) return 'JobMaster';
    if (lowercaseUrl.includes('gotfriends.co.il')) return 'GotFriends';
    if (lowercaseUrl.includes('secrettelaviv.com')) return 'Secret Tel Aviv';
    if (lowercaseUrl.includes('goozali.com')) return 'Goozali';
    if (lowercaseUrl.includes('linkedin.com')) return 'LinkedIn';
    return 'Web Listing';
  };

  const isRtl = (text) => {
    if (!text) return false;
    // Check for Hebrew character range
    return /[\u0590-\u05FF]/.test(text);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      // Replace space with T to make it standard ISO for JS parser
      const date = new Date(dateStr.replace(' ', 'T'));
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    } catch (e) {
      return dateStr;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'starred': return '⭐';
      case 'applied': return '✔️';
      case 'dismissed': return '🗑️';
      default: return '💼';
    }
  };

  const handleRunMatch = async (e) => {
    e.stopPropagation();
    setRunningMatch(true);
    setMatchError('');
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/jobs/${job.id}/match`, {
        method: 'POST',
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to match job');
      }
      const updatedJob = await response.json();
      if (onJobUpdate) {
        onJobUpdate(updatedJob);
      }
    } catch (err) {
      setMatchError(err.message);
    } finally {
      setRunningMatch(false);
    }
  };

  const handleFetchSuggestions = async (e) => {
    e.stopPropagation();
    setLoadingSuggestions(true);
    setErrorSuggestions('');
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/jobs/${job.id}/cv-suggestions`, {
        method: 'POST',
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch suggestions');
      }
      const data = await response.json();
      setSuggestions(data);
    } catch (err) {
      setErrorSuggestions(err.message);
    } finally {
      setLoadingSuggestions(false);
    }
  };

  return (
    <div 
      className={`glass-panel glass-panel-hover job-card ${expanded ? 'expanded' : ''}`}
      style={{
        padding: '1.25rem',
        marginBottom: '1rem',
        cursor: 'pointer',
        transition: 'all 0.3s ease',
        borderLeft: overallScore ? `4px solid ${getScoreColor(overallScore)}` : '4px solid var(--text-muted)'
      }}
      onClick={() => setExpanded(!expanded)}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <span style={{ 
              fontSize: '0.75rem', 
              backgroundColor: 'rgba(139, 92, 246, 0.1)', 
              border: '1px solid rgba(139, 92, 246, 0.2)', 
              padding: '0.15rem 0.5rem', 
              borderRadius: '4px', 
              color: 'var(--accent-purple)', 
              fontWeight: 'bold',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              {getJobSource(job.url)}
            </span>
            <span style={{ fontSize: '0.9rem', backgroundColor: 'var(--bg-tertiary)', padding: '0.15rem 0.5rem', borderRadius: '4px', color: 'var(--text-secondary)' }}>
              {job.company}
            </span>
            <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>📍 {job.location}</span>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginLeft: '0.75rem' }}>
              📅 {formatDate(job.date_found)}
            </span>
          </div>
          <h3 style={{ 
            fontSize: '1.3rem', 
            color: 'var(--text-primary)', 
            marginBottom: '0.5rem',
            direction: isRtl(job.title) ? 'rtl' : 'ltr',
            textAlign: isRtl(job.title) ? 'right' : 'left'
          }}>
            {job.url ? (
              <a 
                href={job.url} 
                target="_blank" 
                rel="noopener noreferrer" 
                style={{ color: 'inherit', textDecoration: 'none', transition: 'color 0.2s' }}
                onMouseEnter={(e) => e.target.style.color = 'var(--accent-purple)'}
                onMouseLeave={(e) => e.target.style.color = 'inherit'}
                onClick={(e) => e.stopPropagation()}
              >
                {job.title} 🔗
              </a>
            ) : (
              job.title
            )}
          </h3>
        </div>
        
        {overallScore !== null ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            backgroundColor: 'rgba(255,255,255,0.03)',
            padding: '0.5rem 0.75rem',
            borderRadius: '8px',
            border: '1px solid rgba(255,255,255,0.05)',
            minWidth: '70px'
          }}>
            <span style={{ fontSize: '1.75rem', fontWeight: 'bold', color: getScoreColor(overallScore) }}>
              {overallScore}%
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Match</span>
          </div>
        ) : (
          <div onClick={(e) => e.stopPropagation()} style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.35rem' }}>
            <button
              onClick={handleRunMatch}
              disabled={runningMatch}
              style={{
                padding: '0.4rem 0.85rem',
                borderRadius: '6px',
                border: 'none',
                background: 'linear-gradient(135deg, var(--accent-purple), var(--accent-blue))',
                color: 'white',
                fontWeight: 'bold',
                cursor: 'pointer',
                fontSize: '0.75rem',
                boxShadow: '0 2px 8px rgba(139, 92, 246, 0.2)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem',
                transition: 'all 0.2s'
              }}
            >
              {runningMatch ? 'Analyzing...' : 'Analyze Match ⚡'}
            </button>
            {matchError && (
              <span style={{ fontSize: '0.65rem', color: 'var(--score-low)', maxWidth: '160px', textAlign: 'right' }}>
                {matchError}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Breakdown Scores */}
      {match && (
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginTop: '0.75rem', fontSize: '0.85rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Tech:</span>
            <strong style={{ color: getScoreColor(match.tech_score) }}>{match.tech_score}</strong>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Data:</span>
            <strong style={{ color: getScoreColor(match.data_score) }}>{match.data_score}</strong>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ color: 'var(--text-secondary)' }}>PM:</span>
            <strong style={{ color: getScoreColor(match.pm_score) }}>{match.pm_score}</strong>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Fit:</span>
            <strong style={{ color: getScoreColor(match.fit_score) }}>{match.fit_score}</strong>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div 
        style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '0.75rem' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button 
            style={{
              padding: '0.35rem 0.75rem',
              borderRadius: '6px',
              border: 'none',
              backgroundColor: job.status === 'starred' ? 'rgba(245, 158, 11, 0.15)' : 'var(--bg-tertiary)',
              color: job.status === 'starred' ? 'var(--score-medium)' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontSize: '0.9rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.25rem'
            }}
            onClick={() => onStatusChange(job.id, job.status === 'starred' ? 'active' : 'starred')}
          >
            ⭐ {job.status === 'starred' ? 'Saved' : 'Save'}
          </button>
          
          <button 
            style={{
              padding: '0.35rem 0.75rem',
              borderRadius: '6px',
              border: 'none',
              backgroundColor: job.status === 'applied' ? 'rgba(16, 185, 129, 0.15)' : 'var(--bg-tertiary)',
              color: job.status === 'applied' ? 'var(--score-high)' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontSize: '0.9rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.25rem'
            }}
            onClick={() => onStatusChange(job.id, job.status === 'applied' ? 'active' : 'applied')}
          >
            ✔️ {job.status === 'applied' ? 'Applied' : 'Mark Applied'}
          </button>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {job.url && (
            <a 
              href={job.url} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="action-btn"
              style={{
                padding: '0.35rem 0.75rem',
                borderRadius: '6px',
                border: '1px solid var(--accent-purple)',
                backgroundColor: 'transparent',
                color: 'var(--accent-purple)',
                textDecoration: 'none',
                fontSize: '0.9rem',
                display: 'flex',
                alignItems: 'center'
              }}
            >
              Apply 🔗
            </a>
          )}
          <button 
            style={{
              padding: '0.35rem 0.75rem',
              borderRadius: '6px',
              border: 'none',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              color: 'var(--score-low)',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
            onClick={() => onStatusChange(job.id, 'dismissed')}
          >
            Dismiss ✖️
          </button>
        </div>
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div 
          style={{ 
            marginTop: '1rem', 
            paddingTop: '1rem', 
            borderTop: '1px solid rgba(255,255,255,0.05)',
            fontSize: '1.0rem',
            animation: 'fadeIn 0.2s ease'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Analysis breakdown */}
          {match && (
            <div style={{ marginBottom: '1.25rem' }}>
              <h4 style={{ color: 'var(--accent-purple)', fontSize: '1.05rem', marginBottom: '0.5rem' }}>💡 AI Matching Analysis</h4>
              <p style={{ 
                color: 'var(--text-primary)', 
                fontStyle: 'italic', 
                marginBottom: '1rem', 
                fontSize: '0.95rem',
                direction: isRtl(match.explanation) ? 'rtl' : 'ltr',
                textAlign: isRtl(match.explanation) ? 'right' : 'left'
              }}>
                &ldquo;{match.explanation || 'No summary available.'}&rdquo;
              </p>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.04)', padding: '0.75rem', borderRadius: '6px', border: '1px solid rgba(16, 185, 129, 0.1)' }}>
                  <strong style={{ color: 'var(--score-high)', fontSize: '0.9rem', display: 'block', marginBottom: '0.25rem' }}>PROS</strong>
                  {match.pros && match.pros.length > 0 ? (
                    <ul style={{ paddingLeft: '1rem', margin: 0, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                      {match.pros.map((pro, i) => <li key={i} style={{ marginBottom: '0.25rem' }}>{pro}</li>)}
                    </ul>
                  ) : <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>None listed</span>}
                </div>
                
                <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.04)', padding: '0.75rem', borderRadius: '6px', border: '1px solid rgba(239, 68, 68, 0.1)' }}>
                  <strong style={{ color: 'var(--score-low)', fontSize: '0.9rem', display: 'block', marginBottom: '0.25rem' }}>CONS / RISK AREAS</strong>
                  {match.cons && match.cons.length > 0 ? (
                    <ul style={{ paddingLeft: '1rem', margin: 0, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                      {match.cons.map((con, i) => <li key={i} style={{ marginBottom: '0.25rem' }}>{con}</li>)}
                    </ul>
                  ) : <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>None listed</span>}
                </div>
              </div>

              {match.red_flags && match.red_flags.length > 0 && (
                <div style={{ backgroundColor: 'rgba(245, 158, 11, 0.06)', padding: '0.75rem', borderRadius: '6px', border: '1px solid rgba(245, 158, 11, 0.15)', marginBottom: '1rem' }}>
                  <strong style={{ color: 'var(--score-medium)', fontSize: '0.9rem', display: 'block', marginBottom: '0.25rem' }}>⚠️ RED FLAGS / RISKS</strong>
                  <ul style={{ paddingLeft: '1rem', margin: 0, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                    {match.red_flags.map((flag, i) => <li key={i} style={{ marginBottom: '0.25rem' }}>{flag}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Job Description */}
          <div style={{ marginBottom: '1.25rem' }}>
            <h4 style={{ color: 'var(--accent-blue)', fontSize: '1.05rem', marginBottom: '0.5rem' }}>📋 Job Description</h4>
            <div style={{ 
              backgroundColor: 'rgba(0,0,0,0.15)', 
              padding: '0.75rem', 
              borderRadius: '6px', 
              color: 'var(--text-secondary)',
              fontSize: '0.9rem',
              whiteSpace: 'pre-wrap',
              maxHeight: '200px',
              overflowY: 'auto',
              direction: isRtl(job.description) ? 'rtl' : 'ltr',
              textAlign: isRtl(job.description) ? 'right' : 'left'
            }}>
              {job.description}
            </div>
          </div>

          {/* On-Demand CV Suggestions */}
          <div style={{ borderTop: '1px dashed rgba(255,255,255,0.08)', paddingTop: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <h4 style={{ color: 'var(--text-primary)', fontSize: '1.05rem' }}>💡 Tailor My CV (On-Demand Suggestions)</h4>
              {!suggestions && (
                <button 
                  onClick={handleFetchSuggestions}
                  disabled={loadingSuggestions}
                  style={{
                    padding: '0.4rem 0.8rem',
                    borderRadius: '6px',
                    border: 'none',
                    backgroundColor: 'var(--accent-purple)',
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: '0.85rem',
                    fontWeight: 'bold',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.25rem'
                  }}
                >
                  {loadingSuggestions ? 'Analyzing...' : 'Generate Phrasing Suggestions ⚡'}
                </button>
              )}
            </div>

            {loadingSuggestions && (
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', padding: '0.5rem', fontStyle: 'italic' }}>
                Comparing CV bullet points against job requirements to formulate suggestions...
              </div>
            )}

            {errorSuggestions && (
              <div style={{ color: 'var(--score-low)', fontSize: '0.9rem', padding: '0.5rem', backgroundColor: 'rgba(239, 68, 68, 0.05)', borderRadius: '4px' }}>
                Failed to generate suggestions: {errorSuggestions}
              </div>
            )}

            {suggestions && (
              <div style={{ backgroundColor: 'rgba(139, 92, 246, 0.03)', border: '1px solid rgba(139, 92, 246, 0.1)', borderRadius: '8px', padding: '0.75rem', fontSize: '0.95rem' }}>
                <p style={{ color: 'var(--text-primary)', marginBottom: '0.75rem', fontStyle: 'italic', fontSize: '0.9rem' }}>
                  &ldquo;{suggestions.general_feedback}&rdquo;
                </p>
                
                {suggestions.suggested_phrasings && suggestions.suggested_phrasings.length > 0 && (
                  <div style={{ marginBottom: '0.75rem' }}>
                    <strong style={{ color: 'var(--accent-purple)', fontSize: '0.9rem', display: 'block', marginBottom: '0.5rem' }}>SUGGESTED REPHRASINGS:</strong>
                    {suggestions.suggested_phrasings.map((phrase, i) => (
                      <div key={i} style={{ backgroundColor: 'rgba(0,0,0,0.1)', padding: '0.5rem', borderRadius: '4px', marginBottom: '0.5rem', fontSize: '0.85rem' }}>
                        <span style={{ fontWeight: 'bold', color: 'var(--text-primary)', display: 'block', marginBottom: '0.25rem' }}>Section: {phrase.section}</span>
                        <div style={{ color: 'var(--score-low)', textDecoration: 'line-through', marginBottom: '0.15rem' }}>From: {phrase.original_text}</div>
                        <div style={{ color: 'var(--score-high)', fontWeight: '500', marginBottom: '0.25rem' }}>To: {phrase.suggested_text}</div>
                        <div style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Rationale: {phrase.rationale}</div>
                      </div>
                    ))}
                  </div>
                )}

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  {suggestions.skills_to_highlight && suggestions.skills_to_highlight.length > 0 && (
                    <div>
                      <strong style={{ color: 'var(--accent-blue)', fontSize: '0.85rem', display: 'block', marginBottom: '0.25rem' }}>ELEVATE THESE SKILLS:</strong>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                        {suggestions.skills_to_highlight.map((skill, i) => (
                          <span key={i} style={{ fontSize: '0.8rem', backgroundColor: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent-blue)', padding: '0.15rem 0.4rem', borderRadius: '4px' }}>
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {suggestions.skills_to_acquire_or_mention && suggestions.skills_to_acquire_or_mention.length > 0 && (
                    <div>
                      <strong style={{ color: 'var(--score-medium)', fontSize: '0.85rem', display: 'block', marginBottom: '0.25rem' }}>MENTION IN INTERVIEW:</strong>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                        {suggestions.skills_to_acquire_or_mention.map((skill, i) => (
                          <span key={i} style={{ fontSize: '0.8rem', backgroundColor: 'rgba(245, 158, 11, 0.1)', color: 'var(--score-medium)', padding: '0.15rem 0.4rem', borderRadius: '4px' }}>
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default JobCard;
