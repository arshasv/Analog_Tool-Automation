import React, { useState, useEffect } from 'react';
import api, { StatusResponse } from '../services/api';
import './Dashboard.css';
import FileUploader from '../components/FileUploader';
import ParameterEditor from '../components/ParameterEditor';
import ResultsViewer from '../components/ResultsViewer';
import ErrorAlert from '../components/ErrorAlert';
import { parseSpiceValue, isValidSpiceValue } from '../utils/spice';

interface Parameter {
  name: string;
  default: any;
  description: string;
  type: string;
}


const Dashboard: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [params, setParams] = useState<Parameter[]>([]);
  const [paramValues, setParamValues] = useState<Record<string, any>>({});
  const [optimizationParams, setOptimizationParams] = useState<Record<string, any>>({});
  const [mode, setMode] = useState<'simulate' | 'optimize'>('simulate');
  const [processId, setProcessId] = useState<string | null>(null);
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [epochs, setEpochs] = useState<number>(30);
  const [activeTab, setActiveTab] = useState<'workflow' | 'results'>('workflow');
  const [optimizedResults, setOptimizedResults] = useState<Record<string, number> | null>(null);
  const [shouldAutoRun, setShouldAutoRun] = useState(false);

  // Auto-run trigger for applied optimization values
  useEffect(() => {
    if (shouldAutoRun && mode === 'simulate' && !loading) {
      setShouldAutoRun(false);
      handleRun();
    }
  }, [shouldAutoRun, mode, loading]);

  // Reset behavior when switching modes
  useEffect(() => {
    if (mode === 'simulate') {
      setOptimizationParams({});
    } else {
      // Clear previous optimization results when starting a new optimize setup
      setOptimizedResults(null);
    }
  }, [mode]);

  // Poll for status
  useEffect(() => {
    let interval: any;
    const currentStatus = status?.status;
    
    if (processId && currentStatus !== 'COMPLETED' && currentStatus !== 'FAILED') {
      interval = setInterval(async () => {
        try {
          const res = await api.getStatus(processId);
          if (res.success && res.data) {
            const newStatusData = res.data;
            setStatus(newStatusData);
            
            if (newStatusData.status === 'COMPLETED' || newStatusData.status === 'SUCCESS') {
               // Capture optimized values if we were in optimize mode
               if (mode === 'optimize' && newStatusData.results?.best_assignment) {
                 setOptimizedResults(newStatusData.results.best_assignment);
               }
               setActiveTab('results');
               clearInterval(interval);
            }
          }
        } catch (err) {
          console.error("Polling error", err);
        }
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [processId, status?.status, mode]);

  const applyOptimizedValues = async (fromResults?: Record<string, any>) => {
    const resultsToApply = fromResults || optimizedResults;
    if (!resultsToApply) return;
    
    setParamValues(prev => ({
      ...prev,
      ...resultsToApply
    }));
    
    setMode('simulate');
    setActiveTab('workflow');
    setOptimizedResults(null); // Clear after applying to keep UI clean

    // If triggered from explicit action (like Results button), we can auto-run
    if (fromResults) {
      setShouldAutoRun(true);
    }
  };

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile);
    setError(null);
    setProcessId(null);
    setStatus(null);
    setParams([]);
    setParamValues({});
    setActiveTab('workflow');
        
    if (selectedFile.name.endsWith('.py')) {
      setLoading(true);
      try {
        const res = await api.introspect(selectedFile);
        setLoading(false);
        if (res.success && res.data && res.data.parameters) {
          const rawParams = res.data.parameters;
          let formattedParams: Parameter[] = [];
          const defaults: Record<string, any> = {};
          if (Array.isArray(rawParams)) {
            formattedParams = rawParams;
            rawParams.forEach((p: any) => {
              if (p && p.name) defaults[p.name] = p.default;
            });
          } else if (typeof rawParams === 'object') {
            formattedParams = Object.entries(rawParams).map(([key, val]) => ({
              name: key,
              default: val,
              type: typeof val,
              description: `Default value: ${val}`
            }));
            Object.entries(rawParams).forEach(([key, val]) => {
              defaults[key] = val;
            });
          }
          setParams(formattedParams);
          setParamValues(defaults);
        } else {
          setError(res.error || 'Failed to introspect file');
        }
      } catch (err) {
        setLoading(false);
        setError("Error processing file introspect");
      }
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setParams([]);
    setParamValues({});
    setOptimizationParams({});
    setError(null);
    setProcessId(null);
    setStatus(null);
  };

  const handleParamChange = (name: string, value: any) => {
    setParamValues(prev => ({ ...prev, [name]: value }));
    if (fieldErrors[name]) {
      setFieldErrors(prev => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const handleOptParamChange = (name: string, field: string, value: any) => {
    setOptimizationParams(prev => ({
      ...prev,
      [name]: {
        ...(prev[name] || {}),
        [field]: value
      }
    }));
    const errorKey = field === 'target' ? `${name}_target` : name;
    if (fieldErrors[errorKey]) {
      setFieldErrors(prev => {
        const next = { ...prev };
        delete next[errorKey];
        return next;
      });
    }
  };

  const handleRun = async () => {
    if (!file) return;

    // Clear previous errors
    setFieldErrors({});

    // Parameter Validation
    const newFieldErrors: Record<string, string> = {};
    let hasErrors = false;

    for (const [name, val] of Object.entries(paramValues)) {
      // Find the parameter definition to check its type
      const paramDef = params.find(p => p.name === name);
      const isStringParam = paramDef?.type.toLowerCase() === 'string';

      if (!isStringParam && typeof val === 'string' && val.trim() !== '' && !isValidSpiceValue(val)) {
        newFieldErrors[name] = "Invalid format. Use numeric values (e.g., 10u, 1.2).";
        hasErrors = true;
      }
    }

    if (mode === 'optimize') {
      // Validate optimization targets
      for (const [name, opt] of Object.entries(optimizationParams)) {
        if (opt.target && !isValidSpiceValue(opt.target)) {
          newFieldErrors[`${name}_target`] = "Invalid target format.";
          hasErrors = true;
        }
        if (opt.initial && !isValidSpiceValue(opt.initial)) {
          newFieldErrors[name] = "Invalid initial format.";
          hasErrors = true;
        }
      }

      // Epoch Validation
      if (epochs < 1 || epochs > 200) {
        setError("Epoch value must be between 1 and 200.");
        return;
      }
    }

    if (hasErrors) {
      setFieldErrors(newFieldErrors);
      setError("Please fix the validation errors below.");
      return;
    }

    setLoading(true);
    setError(null);
    setProcessId(null); // Reset process ID to trigger UI clear before new run
    try {
      let res;
      if (mode === 'optimize') {
        const optPayload = {
          epochs: epochs,
          target_current: paramValues['target_current'] !== undefined ? parseSpiceValue(paramValues['target_current']) : undefined,
          target_gain: paramValues['target_gain'] !== undefined ? parseSpiceValue(paramValues['target_gain']) : undefined,
          params: Object.fromEntries(
            Object.entries(optimizationParams).map(([name, opt]) => [
              name,
              { target: parseSpiceValue(opt.target), initial: parseSpiceValue(opt.initial) }
            ])
          )
        };
        res = await api.run(file, mode, optPayload);
      } else {
        // Also parse regular simulation parameters just in case
        const parsedParams = Object.fromEntries(
          Object.entries(paramValues).map(([k, v]) => [k, typeof v === 'string' ? parseSpiceValue(v) : v])
        );
        res = await api.run(file, mode, parsedParams);
      }

      setLoading(false);
      if (res.success && res.data) {
        setProcessId(res.data.process_id);
        setStatus({ process_id: res.data.process_id, status: 'PENDING', updated_at: new Date().toISOString() } as StatusResponse);
      } else {
        setError(res.error || 'Failed to start job');
      }
    } catch (err) {
      setLoading(false);
      setError("Error starting job");
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-shell">
        <div className="nav-toggle">
           <button 
             className={activeTab === 'workflow' ? 'active' : ''} 
             onClick={() => setActiveTab('workflow')}
           >
             Workflow
           </button>
           <button 
             className={activeTab === 'results' ? 'active' : ''} 
             onClick={() => setActiveTab('results')}
           >
             Results
           </button>
        </div>

        <aside className="dashboard-kpi-bar">
          <div className="kpi-item">
            <label className="label-uppercased">Workflow ID</label>
            <span className="mono">{processId ? processId : '---'}</span>
          </div>
          <div className="kpi-item">
            <label className="label-uppercased">Status</label>
            <span className={`status-text-${status?.status.toLowerCase() || 'none'} kpi-value`}>
              {status ? (status.status.charAt(0).toUpperCase() + status.status.slice(1).toLowerCase()) : 'Inactive'}
            </span>
          </div>
          <div className="kpi-item">
            <label className="label-uppercased">Mode</label>
            <span className="kpi-value">{mode === 'simulate' ? 'Simulate' : 'Optimize'}</span>
          </div>
        </aside>

        {error && !error.includes("Epoch value must be between 1 and 200.") && <ErrorAlert message={error} onDismiss={() => setError(null)} />}

        {activeTab === 'workflow' ? (
          <section className="dashboard-workspace">
            <div className="dashboard-primary-column">
              <article className="dashboard-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Circuit file</h2>
                  </div>
                </div>
                <FileUploader onFileSelect={handleFileSelect} onRemoveFile={handleRemoveFile} selectedFile={file} />
              </article>

              {loading && <div className="loading-overlay">Processing...</div>}

              {params.length > 0 && (
                <article className="dashboard-panel">
                  <div className="panel-heading">
                    <div>
                      <h2>Specifications</h2>
                    </div>
                  </div>
                  <ParameterEditor 
                    parameters={params} 
                    values={paramValues} 
                    onChange={handleParamChange}
                    optimizationParams={optimizationParams}
                    onOptParamChange={handleOptParamChange}
                    mode={mode}
                    errors={fieldErrors}
                  />
                </article>
              )}

              {mode === 'optimize' && (
                <article className="dashboard-panel">
                  <div className="panel-heading">
                    <div>
                      <h2>Search Strategy</h2>
                    </div>
                  </div>
                  <div className="param-input-container">
                    <label>Epochs (Iterations)</label>
                    <input
                      type="number"
                      className={`dashboard-input ${error && error.includes('Epoch value must be between 1 and 200.') ? 'input-error' : ''}`}
                      value={epochs}
                      min={1}
                      max={200}
                      onChange={(e) => {
                        setEpochs(parseInt(e.target.value) || 0);
                        if (error && error.includes('Epoch value must be between 1 and 200.')) setError(null);
                      }}
                      style={{ width: '100px' }}
                    />
                    {error && error.includes('Epoch value must be between 1 and 200.') && (
                      <div className="input-error-message" style={{ color: 'var(--error)', fontSize: '0.85rem', marginTop: '4px', fontWeight: 'bold' }}>
                        ⚠️ {error}
                      </div>
                    )}
                    <small className="muted" style={{ display: 'block', marginTop: '4px' }}>
                      Valid range: 1 - 200. Higher values increase accuracy but take longer.
                    </small>
                  </div>
                </article>
              )}

              <article className="dashboard-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Mode selection</h2>
                  </div>
                </div>
                <div className="mode-toggle-group">
                  <button 
                    className={`mode-toggle-button ${mode === 'simulate' ? 'mode-toggle-button-active' : ''}`}
                    onClick={() => setMode('simulate')}
                  >
                    SIMULATE
                  </button>
                  <button 
                    className={`mode-toggle-button ${mode === 'optimize' ? 'mode-toggle-button-active' : ''}`}
                    onClick={() => setMode('optimize')}
                  >
                    OPTIMIZE
                  </button>
                </div>
                <button 
                  className="dashboard-primary-action" 
                  onClick={handleRun}
                  disabled={!file || loading || status?.status === 'RUNNING' || status?.status === 'PENDING'}
                >
                   {loading || status?.status === 'RUNNING' || status?.status === 'PENDING' 
                    ? (loading ? 'STARTING...' : 'RUNNING...') 
                    : `RUN ${mode.toUpperCase()}`}
                </button>

                {/* LIVE STATUS component placed directly below the run button */}
                {processId && (
                  <article className="dashboard-panel" style={{ marginTop: '1.5rem', borderLeft: '4px solid var(--accent)' }}>
                    <div className="panel-heading" style={{ marginBottom: '1rem' }}>
                      <div>
                        <span className="panel-eyebrow">LIVE STATUS</span>
                        <h2 style={{ fontSize: '1rem', wordBreak: 'break-all' }}>
                          ID : {file ? file.name : 'Unknown'}_{processId.slice(0, 8)}
                        </h2>
                      </div>
                      <span className={`results-status-pill results-status-pill-${status?.status.toLowerCase()}`}>
                        {status?.status ? status.status.charAt(0).toUpperCase() + status.status.slice(1).toLowerCase() : ''}
                      </span>
                    </div>

                    <div className="status-timeline" style={{ maxHeight: '200px', overflowY: 'auto', fontSize: '0.85rem' }}>
                      {status && (
                        <div className="status-update" style={{ display: 'flex', gap: '12px', padding: '8px 0' }}>
                          <span className="muted">{new Date(status.updated_at).toLocaleTimeString()}</span>
                          <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <strong style={{ color: 'var(--accent)' }}>{status.status}</strong>
                            {status.progress !== undefined && (
                              <div style={{ width: '100%', background: 'var(--status-pill-bg)', height: '4px', borderRadius: '2px', marginTop: '4px' }}>
                                <div style={{ width: `${status.progress}%`, background: 'var(--accent)', height: '100%', borderRadius: '2px' }} />
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                      
                      {/* Filtering out "Worker update received" and showing meaningful logs */}
                      <div className="status-logs">
                        {status?.status === 'RUNNING' && <p style={{ margin: '4px 0' }}>{mode === 'optimize' ? 'HEURISTIC SEARCH IN PROGRESS...' : 'CALCULATING OPERATING POINT...'}</p>}
                        {status?.status === 'COMPLETED' && <p style={{ margin: '4px 0', color: 'var(--success)' }}>EXECUTION SUCCESSFUL.</p>}
                        {status?.status === 'FAILED' && <p style={{ margin: '4px 0', color: 'var(--error)' }}>{status.error || 'ANALYSIS FAILED.'}</p>}
                      </div>
                    </div>

                    {(status?.status === 'COMPLETED' || status?.status === 'SUCCESS' || status?.status === 'FAILED') && (
                      <button 
                        className="dashboard-primary-action"
                        style={{ marginTop: '1rem', background: 'transparent', border: '1px solid var(--accent)', color: 'var(--accent)', padding: '8px' }}
                        onClick={() => setActiveTab('results')}
                      >
                        VIEW RESULTS
                      </button>
                    )}
                  </article>
                )}
              </article>
            </div>

            <div className="dashboard-secondary-column">
              {optimizedResults && (
                <article className="dashboard-panel" style={{ border: '1px solid var(--accent)', background: 'var(--status-pill-bg)' }}>
                  <div className="panel-heading">
                    <div>
                      <span className="panel-eyebrow">OPTIMIZATION</span>
                      <h2>Best Assignment</h2>
                    </div>
                  </div>
                  <div style={{ margin: '1rem 0' }}>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                      {Object.entries(optimizedResults).map(([key, value]) => (
                        <li key={key} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid var(--border)' }}>
                          <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600, color: 'var(--text-muted)' }}>{key.replace(/_/g, ' ')}</span>
                          <strong style={{ color: 'var(--accent)' }}>
                            {typeof value === 'number' ? value.toFixed(3) : value}
                          </strong>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <button 
                    className="dashboard-primary-action"
                    onClick={applyOptimizedValues}
                  >
                    Use Optimized Values
                  </button>
                </article>
              )}
            </div>

          </section>
        ) : (
          <section className="dashboard-results-view">
             <article className="dashboard-panel">
                <ResultsViewer 
                  status={status!} 
                  onApplyOptimized={(p) => applyOptimizedValues(p)}
                />
             </article>
          </section>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
