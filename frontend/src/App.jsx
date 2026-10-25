import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  BookOpen,
  Volume2,
  Video,
  Trophy,
  Compass,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Download,
  Flame,
  Award,
  Library,
  GraduationCap
} from 'lucide-react';

const PRESET_MORALS = [
  "Honesty builds trust that deceit permanently destroys.",
  "Kindness is never wasted, no matter how small the act.",
  "Pride blinds the mind right before a dangerous fall.",
  "Patience turns heavy obstacles into lasting triumphs.",
  "True wealth is not what you hoard, but what you share.",
  "Courage is not the absence of fear, but acting despite it."
];

export default function App() {
  const [activeTab, setActiveTab] = useState('studio');
  const [moral, setMoral] = useState(PRESET_MORALS[0]);
  const [topic, setTopic] = useState('');
  const [models, setModels] = useState(['qwen2.5:3b', 'qwen3:8b']);
  const [selectedModel, setSelectedModel] = useState('qwen2.5:3b');
  const [baselineModel, setBaselineModel] = useState('qwen3:8b');
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState('af_heart');
  const [mode, setMode] = useState('tournament');
  const [candidates, setCandidates] = useState(3);
  const [generateAudio, setGenerateAudio] = useState(true);
  const [generateVideo, setGenerateVideo] = useState(true);

  const [loading, setLoading] = useState(false);
  const [stepStatus, setStepStatus] = useState('');
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  // Library & Study states
  const [savedStories, setSavedStories] = useState([]);
  const [studyTrials, setStudyTrials] = useState(1);
  const [fineTunedModel, setFineTunedModel] = useState('');
  const [fastStudy, setFastStudy] = useState(true);
  const [studyLoading, setStudyLoading] = useState(false);
  const [studySummary, setStudySummary] = useState(null);

  const fineTunedOptions = models.filter(
    (model) => model !== selectedModel && model !== baselineModel
  );

  useEffect(() => {
    // Fetch models
    fetch('/api/models')
      .then(res => res.json())
      .then(data => {
        if (data.models && data.models.length > 0) {
          setModels(data.models);
          setSelectedModel(data.default || data.models[0]);
          setBaselineModel(data.baseline || data.default || data.models[0]);
        }
      })
      .catch(() => {});

    // Fetch voices
    fetch('/api/voices')
      .then(res => res.json())
      .then(data => {
        if (data.voices) {
          setVoices(data.voices);
          setSelectedVoice(data.default || data.voices[0].id);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
      if (fineTunedModel && !fineTunedOptions.includes(fineTunedModel)) {
        setFineTunedModel('');
      }
  }, [selectedModel, models, fineTunedModel, fineTunedOptions]);

  const loadSavedStories = () => {
    fetch('/api/stories')
      .then(res => res.json())
      .then(data => setSavedStories(data.stories || []))
      .catch(() => {});
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setStepStatus('Initializing Ollama & Generating Candidate Stories...');

    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          moral: moral.trim(),
          topic: topic.trim() || null,
          mode,
          candidates,
          model: selectedModel,
          voice: selectedVoice,
          generate_audio: generateAudio,
          generate_video: generateVideo
        })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server returned ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
      setStepStatus('Complete!');
    } catch (err) {
      setError(err.message || 'Generation failed. Make sure Ollama and backend server are running.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunStudy = async () => {
    setStudyLoading(true);
    try {
      const res = await fetch('/api/study', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          trials: studyTrials,
          fine_tuned_model: fineTunedModel.trim() || null,
          fast: fastStudy
        })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || `Benchmark failed (${res.status})`);
      }
      setStudySummary(data.summary);
    } catch (err) {
      alert('Study execution failed: ' + err.message);
    } finally {
      setStudyLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header Banner */}
      <header className="header-banner">
        <div>
          <div className="brand-title">
            <span>⚡ AI-Story-Engine</span>
            <span className="brand-badge">Moral Fables Studio</span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginTop: '6px' }}>
            Agentic Short-Form Video Pipeline: Moral-driven educational story generation, quality critique, and vertical video rendering.
          </p>
        </div>
        <div>
          <div className="status-pill">
            <span className="status-dot"></span>
            <span>Local Engine Active</span>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="nav-tabs">
        <button
          className={`nav-tab-btn ${activeTab === 'studio' ? 'active' : ''}`}
          onClick={() => setActiveTab('studio')}
        >
          <Sparkles size={18} />
          <span>Creator Studio</span>
        </button>
        <button
          className={`nav-tab-btn ${activeTab === 'library' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('library');
            loadSavedStories();
          }}
        >
          <BookOpen size={18} />
          <span>Story Library</span>
        </button>
        <button
          className={`nav-tab-btn ${activeTab === 'study' ? 'active' : ''}`}
          onClick={() => setActiveTab('study')}
        >
          <GraduationCap size={18} />
          <span>RAG vs. Base Study</span>
        </button>
      </nav>

      {/* ============================================================== */}
      {/* TAB 1: CREATOR STUDIO */}
      {/* ============================================================== */}
      {activeTab === 'studio' && (
        <div>
          <div className="grid-2col">
            {/* Left Column: Moral & Setting Input */}
            <div className="card">
              <h2 className="card-title">
                <Compass size={20} color="#818cf8" />
                <span>1. Core Moral & Premise</span>
              </h2>

              <label className="input-label">Target Moral / Life Lesson (The core truth delivered at the end):</label>
              
              <div className="chips-row">
                {PRESET_MORALS.map((m, i) => (
                  <button
                    key={i}
                    type="button"
                    className="chip-btn"
                    onClick={() => setMoral(m)}
                  >
                    "{m.split(' ')[0]} {m.split(' ')[1]}..."
                  </button>
                ))}
              </div>

              <textarea
                className="text-input"
                style={{ height: '76px', resize: 'vertical', marginBottom: '16px' }}
                value={moral}
                onChange={(e) => setMoral(e.target.value)}
                placeholder="Enter the core moral lesson the story must prove..."
              />

              <label className="input-label">Optional Setting or Character Context:</label>
              <input
                type="text"
                className="text-input"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. An ambitious young apprentice in a clockmaker's workshop..."
              />
            </div>

            {/* Right Column: Engine & Audio Configuration */}
            <div className="card">
              <h2 className="card-title">
                <Award size={20} color="#818cf8" />
                <span>2. Engine & Model Config</span>
              </h2>

              <div style={{ marginBottom: '14px' }}>
                <label className="input-label">Ollama LLM Model:</label>
                <select
                  className="select-input"
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                >
                  {models.map(m => (
                    <option key={m} value={m}>
                      {m} {m.includes('3b') ? '⚡ (Fast ~15s)' : '🧠 (Deep 8B)'}
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '14px' }}>
                <div>
                  <label className="input-label">Pipeline Mode:</label>
                  <select
                    className="select-input"
                    value={mode}
                    onChange={(e) => setMode(e.target.value)}
                  >
                    <option value="tournament">Tournament (Best-of-N)</option>
                    <option value="rewrite">Iterative Rewrite</option>
                    <option value="single">Single Fast Draft</option>
                  </select>
                </div>
                <div>
                  <label className="input-label">Candidate Stories:</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    className="text-input"
                    disabled={mode !== 'tournament'}
                    value={candidates}
                    onChange={(e) => setCandidates(parseInt(e.target.value) || 3)}
                  />
                </div>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label className="input-label">Kokoro TTS Voice:</label>
                <select
                  className="select-input"
                  value={selectedVoice}
                  onChange={(e) => setSelectedVoice(e.target.value)}
                >
                  {voices.map(v => (
                    <option key={v.id} value={v.id}>{v.name}</option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'flex', gap: '20px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.9rem' }}>
                  <input
                    type="checkbox"
                    checked={generateAudio}
                    onChange={(e) => setGenerateAudio(e.target.checked)}
                  />
                  <span>Voiceover (Kokoro)</span>
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.9rem' }}>
                  <input
                    type="checkbox"
                    checked={generateVideo}
                    onChange={(e) => setGenerateVideo(e.target.checked)}
                  />
                  <span>9:16 Video Short</span>
                </label>
              </div>
            </div>
          </div>

          {/* Primary Action Button */}
          <button
            className="btn-primary-action"
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="spinner"></div>
                <span>Generating Educational Short...</span>
              </>
            ) : (
              <>
                <Sparkles size={20} />
                <span>Generate Moral Story & Short</span>
              </>
            )}
          </button>

          {/* Live Progress / Status Card */}
          {loading && (
            <div className="stepper-box">
              <div className="step-item active">
                <div className="spinner"></div>
                <span>{stepStatus}</span>
              </div>
              <div className="step-item">
                <Trophy size={16} />
                <span>AI Critic evaluating Moral Clarity & Viral Retention...</span>
              </div>
              <div className="step-item">
                <Volume2 size={16} />
                <span>Kokoro Neural Speech Synthesis (24kHz)...</span>
              </div>
              <div className="step-item">
                <Video size={16} />
                <span>Video Agent Compositing 9:16 Short with Subtitles...</span>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div style={{ marginTop: '20px', padding: '16px', borderRadius: '8px', background: '#451a1a', border: '1px solid #dc2626', color: '#fca5a5' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold' }}>
                <AlertCircle size={20} />
                <span>Execution Error</span>
              </div>
              <p style={{ marginTop: '6px', fontSize: '0.95rem' }}>{error}</p>
            </div>
          )}

          {/* ============================================================== */}
          {/* RESULTS DISPLAY */}
          {/* ============================================================== */}
          {result && result.story && (
            <div style={{ marginTop: '36px' }}>
              {/* Highlighted Moral Banner */}
              <div className="moral-banner">
                <span className="moral-banner-icon">💡</span>
                <div>
                  <div className="moral-banner-title">Core Moral of the Story</div>
                  <div className="moral-banner-text">"{result.story.moral}"</div>
                </div>
              </div>

              {/* Hook Card */}
              <div className="hook-box">
                <strong>⚡ HOOK (0-5s):</strong> "{result.story.hook}"
              </div>

              {/* Story Narrative vs Critic Scorecard */}
              <div className="grid-2col">
                {/* Left: Narrative */}
                <div className="card">
                  <h3 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff', marginBottom: '14px' }}>
                    📖 {result.story.title}
                  </h3>
                  
                  <div className="story-body">
                    {result.story.story}
                  </div>

                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    📊 Word Count: <strong>{result.story.story.split(/\s+/).length} words</strong> • Ending with Core Moral Delivery
                  </div>

                  <div style={{ marginTop: '20px' }}>
                    <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#818cf8', marginBottom: '8px' }}>
                      🖼️ Scene Prompts (Visual Narrative Progression):
                    </h4>
                    {result.story.scene_prompts && result.story.scene_prompts.map((sc, i) => (
                      <div key={i} style={{ fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '6px', paddingLeft: '10px', borderLeft: '2px solid #4f46e5' }}>
                        <strong>Scene {i + 1}:</strong> {sc}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Right: AI Critic 9-Dimension Evaluation */}
                <div className="card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 className="card-title" style={{ margin: 0 }}>
                      <Trophy size={20} color="#f59e0b" />
                      <span>AI Critic Scorecard</span>
                    </h3>
                    <span className="status-pill" style={{ background: '#312e81', color: '#c7d2fe', borderColor: '#4f46e5' }}>
                      Score: {result.review?.scores?.overall?.toFixed(1) || '8.0'} / 10
                    </span>
                  </div>

                  {/* 9 Dimensions */}
                  {[
                    ['Moral Clarity', result.review?.scores?.moral_clarity ?? 8.5],
                    ['Hook Strength', result.review?.scores?.hook ?? 8.0],
                    ['Pacing & Flow', result.review?.scores?.pacing ?? 8.0],
                    ['Emotional Impact', result.review?.scores?.emotion ?? 7.5],
                    ['Believability', result.review?.scores?.believability ?? 8.5],
                    ['Audience Retention', result.review?.scores?.retention ?? 8.0],
                    ['Originality', result.review?.scores?.originality ?? 8.0],
                    ['AI Naturalness', result.review?.scores?.ai_naturalness ?? 8.5],
                    ['Comment Potential', result.review?.scores?.comment_potential ?? 8.0]
                  ].map(([label, score], idx) => (
                    <div key={idx} className="dim-row">
                      <div className="dim-header">
                        <span>{label}</span>
                        <span className="dim-val">{Number(score).toFixed(1)}</span>
                      </div>
                      <div className="progress-track">
                        <div
                          className="progress-fill"
                          style={{ width: `${Math.min(100, Math.max(0, (score / 10) * 100))}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}

                  {result.review?.feedback && (
                    <div style={{ marginTop: '16px', padding: '12px', background: '#0f172a', borderRadius: '8px', fontSize: '0.88rem', color: '#cbd5e1' }}>
                      <strong>Critic Feedback:</strong> {result.review.feedback}
                    </div>
                  )}
                </div>
              </div>

              {/* Media Players Section */}
              <div className="media-grid">
                {/* Audio Player */}
                <div className="media-card">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', fontWeight: 'bold' }}>
                    <Volume2 size={20} color="#818cf8" />
                    <span>Kokoro Voiceover Audio (24kHz)</span>
                  </div>
                  {result.audio_url ? (
                    <div>
                      <audio controls style={{ width: '100%', borderRadius: '8px' }} src={result.audio_url} />
                      <a href={result.audio_url} download className="btn-download">
                        <Download size={16} />
                        <span>Download Audio (WAV)</span>
                      </a>
                    </div>
                  ) : (
                    <p style={{ color: 'var(--text-dim)', fontSize: '0.9rem' }}>Audio generation skipped.</p>
                  )}
                </div>

                {/* Video Player */}
                <div className="media-card">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', fontWeight: 'bold' }}>
                    <Video size={20} color="#f59e0b" />
                    <span>Vertical Short Video (1080x1920)</span>
                  </div>
                  {result.video_url ? (
                    <div>
                      <video controls style={{ width: '100%', maxHeight: '360px', borderRadius: '8px', background: '#000' }} src={result.video_url} />
                      <a href={result.video_url} download className="btn-download">
                        <Download size={16} />
                        <span>Download 9:16 MP4 Video</span>
                      </a>
                    </div>
                  ) : (
                    <p style={{ color: 'var(--text-dim)', fontSize: '0.9rem' }}>Video rendering skipped.</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ============================================================== */}
      {/* TAB 2: STORY LIBRARY */}
      {/* ============================================================== */}
      {activeTab === 'library' && (
        <div className="card">
          <h2 className="card-title">
            <Library size={22} color="#818cf8" />
            <span>Saved Educational Stories Archive</span>
          </h2>

          {savedStories.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No stories found in data/stories/. Generate some in Creator Studio!</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {savedStories.map((s) => (
                <div key={s.id} style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '10px', padding: '18px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff' }}>
                        #{s.id}: {s.title}
                      </h3>
                      <div style={{ color: '#f59e0b', fontWeight: 600, fontSize: '0.92rem', marginTop: '4px' }}>
                        💡 Moral: "{s.moral}"
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '10px' }}>
                      {s.audio_url && (
                        <a href={s.audio_url} target="_blank" rel="noreferrer" className="chip-btn">
                          ▶ Listen Audio
                        </a>
                      )}
                      {s.video_url && (
                        <a href={s.video_url} target="_blank" rel="noreferrer" className="chip-btn" style={{ background: '#312e81', color: '#c7d2fe' }}>
                          ▶ Watch Video
                        </a>
                      )}
                    </div>
                  </div>

                  <p style={{ marginTop: '12px', color: '#cbd5e1', fontSize: '0.95rem', lineHeight: '1.6' }}>
                    {s.story}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ============================================================== */}
      {/* TAB 3: EXTENSION STUDY */}
      {/* ============================================================== */}
      {activeTab === 'study' && (
        <div className="card">
          <h2 className="card-title">
            <GraduationCap size={22} color="#818cf8" />
            <span>Academic Extension Study: RAG vs. Fine-Tuning Benchmark</span>
          </h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: '18px' }}>
            Compare baseline prompting, Retrieval-Augmented Generation (RAG), and a local fine-tuned Ollama model using the same critic metrics.
          </p>

          <div style={{ display: 'flex', gap: '16px', alignItems: 'center', marginBottom: '20px' }}>
            <label className="input-label" style={{ margin: 0 }}>Trials per Method:</label>
            <input
              type="number"
              min="1"
              max="5"
              className="text-input"
              style={{ width: '80px' }}
              value={studyTrials}
              onChange={(e) => setStudyTrials(parseInt(e.target.value) || 1)}
            />
            <label className="input-label" style={{ margin: 0 }}>Fine-tuned Ollama model:</label>
            <select
              className="text-input"
              style={{ width: '220px' }}
              value={fineTunedModel}
              onChange={(e) => setFineTunedModel(e.target.value)}
            >
              <option value="">Select an installed fine-tuned model</option>
              {fineTunedOptions.map((model) => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>
              Only models returned by Ollama are listed; the selected baseline is excluded.
            </span>
            <label style={{ color: 'var(--text-muted)' }}>
              <input type="checkbox" checked={fastStudy} onChange={(e) => setFastStudy(e.target.checked)} />
              {' '}Fast mode
            </label>
            <button
              className="chip-btn"
              style={{ background: 'var(--primary)', color: '#fff', padding: '10px 18px', fontWeight: 600 }}
              onClick={handleRunStudy}
              disabled={studyLoading}
            >
              {studyLoading ? 'Running Benchmark Trials...' : 'Run Comparative Benchmark'}
            </button>
          </div>

          {studySummary && (
            <div style={{ marginTop: '24px' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '12px' }}>Benchmark Results Summary</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #334155', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '10px' }}>Evaluation Metric</th>
                    <th style={{ padding: '10px' }}>Baseline</th>
                    <th style={{ padding: '10px' }}>RAG</th>
                    <th style={{ padding: '10px' }}>Fine-Tuned</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(studySummary).map(([metric, data]) => {
                    if (metric === '_notice') {
                      return (
                        <tr key={metric}>
                          <td colSpan="4" style={{ padding: '10px', color: '#fbbf24' }}>
                            {data.rag_avg}
                          </td>
                        </tr>
                      );
                    }
                    if (metric === '_errors') {
                      return (
                        <tr key={metric}>
                          <td colSpan="4" style={{ padding: '10px', color: '#f87171' }}>
                            {Object.entries(data).map(([method, error]) => (
                              <div key={method}><strong>{method}:</strong> {error}</div>
                            ))}
                          </td>
                        </tr>
                      );
                    }
                    const delta = (data.rag_avg - data.baseline_avg).toFixed(2);
                    return (
                      <tr key={metric} style={{ borderBottom: '1px solid #1e293b' }}>
                        <td style={{ padding: '10px', fontWeight: 600, textTransform: 'capitalize' }}>{metric}</td>
                        <td style={{ padding: '10px' }}>{data.baseline_avg.toFixed(2)}</td>
                        <td style={{ padding: '10px' }}>{data.rag_avg.toFixed(2)}</td>
                        <td style={{ padding: '10px' }}>{data.fine_tuned_avg.toFixed(2)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
