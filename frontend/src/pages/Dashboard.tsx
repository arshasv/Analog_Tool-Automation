import React, { useState, useEffect } from 'react';
import { Play, LayoutGrid } from 'lucide-react';
import api, { StatusResponse } from '../services/api';
import './Dashboard.css';
import FileUploader from '../components/FileUploader';
import ParameterEditor from '../components/ParameterEditor';
import ResultsViewer from '../components/ResultsViewer';
import ErrorAlert from '../components/ErrorAlert';
import { parseSpiceValue, isValidSpiceValue, requiresPositiveValue, isNegativeValue } from '../utils/spice';

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
  const [epochInput, setEpochInput] = useState<string>('30');
  const [activeTab, setActiveTab] = useState<'workflow' | 'results'>('workflow');
  const [optimizedResults, setOptimizedResults] = useState<Record<string, number> | null>(null);
  const [shouldAutoRun, setShouldAutoRun] = useState(false);

  // Automatically scroll to top when opening/navigating dashboard
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Scroll to top when showing Results view
  useEffect(() => {
    if (activeTab === 'results') {
      // ensure the results view starts at top
      window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
    }
  }, [activeTab]);

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

      if (!isStringParam && typeof val === 'string' && val.trim() !== '') {
        // Check if valid SPICE format
        if (!isValidSpiceValue(val)) {
          newFieldErrors[name] = "Invalid format. Use numeric values (e.g., 10u, 1.2).";
          hasErrors = true;
        }
        // Check if parameter requires positive value (W, L, R, C)
        else if (requiresPositiveValue(name) && isNegativeValue(val)) {
          newFieldErrors[name] = `This parameter must be positive. Example: 2.5u (not ${val})`;
          hasErrors = true;
        }
      }
    }

    if (mode === 'optimize') {
      // Validate optimization targets
      for (const [name, opt] of Object.entries(optimizationParams)) {
        if (opt.target && !isValidSpiceValue(opt.target)) {
          newFieldErrors[`${name}_target`] = "Invalid target format.";
          hasErrors = true;
        } else if (opt.target && requiresPositiveValue(name) && isNegativeValue(opt.target)) {
          newFieldErrors[`${name}_target`] = `Target must be positive for this parameter.`;
          hasErrors = true;
        }
        
        if (opt.initial && !isValidSpiceValue(opt.initial)) {
          newFieldErrors[name] = "Invalid initial format.";
          hasErrors = true;
        } else if (opt.initial && requiresPositiveValue(name) && isNegativeValue(opt.initial)) {
          newFieldErrors[name] = `Initial value must be positive. Example: 2.5u (not ${opt.initial})`;
          hasErrors = true;
        }
      }

      // Epoch Validation
      const epochVal = parseInt(epochInput);
      if (isNaN(epochVal) || epochVal < 1 || epochVal > 200) {
        setError("Epoch value must be between 1 and 200. Example: 50");
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
          epochs: parseInt(epochInput) || 30,
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
        <div className="dashboard-nav-header">
          <div className="nav-toggle" style={{ border: 'none', marginBottom: 0, width: 'auto' }}>
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
        </div>

        <aside className="dashboard-kpi-bar" style={{ paddingBottom: '2rem' }}>
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
                    <h2>Circuit upload</h2>
                  </div>
                </div>
                <FileUploader onFileSelect={handleFileSelect} onRemoveFile={handleRemoveFile} selectedFile={file} />
                
                <div className="simulate-optimize-toggle">
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
                </div>
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
                    disableWL={
                      loading ||
                      shouldAutoRun ||
                      ['PENDING', 'RUNNING'].includes((status?.status || '').toUpperCase())
                    }
                  />
                </article>
              )}

              {mode === 'optimize' && (
                <article className="dashboard-panel">
                  <div className="panel-heading">
                    <div>
                      <h2>Target Specifications</h2>
                    </div>
                  </div>
                  <div className="param-input-container">
                    <label>Epochs (Iterations)</label>
                    <input
                      type="text"
                      className={`dashboard-input ${error && error.includes('Epoch value must be between 1 and 200.') ? 'input-error' : ''}`}
                      value={epochInput}
                      onChange={(e) => {
                        setEpochInput(e.target.value);
                        if (error && error.includes('Epoch value must be between 1 and 200.')) setError(null);
                      }}
                      onBlur={() => {
                        const val = parseInt(epochInput);
                        if (!isNaN(val)) {
                          if (val < 1) setEpochInput('1');
                          if (val > 200) setEpochInput('200');
                        } else if (epochInput !== '') {
                          setEpochInput('30');
                        }
                      }}
                      style={{ width: '100px' }}
                      placeholder="Ex: 30"
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

              {params.length > 0 && (
                <div className="dashboard-sticky-actions">
                  <button 
                    className="dashboard-primary-action" 
                    onClick={handleRun}
                    disabled={!file || loading || status?.status === 'RUNNING' || status?.status === 'PENDING'}
                    style={{ flex: 2 }}
                  >
                    {loading || status?.status === 'RUNNING' || status?.status === 'PENDING' 
                      ? (loading ? 'STARTING...' : 'RUNNING...') 
                      : (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                          <Play size={18} fill="currentColor" />
                          <span>{mode === 'simulate' ? 'RUN SIMULATION' : 'RUN OPTIMIZATION'}</span>
                        </div>
                      )}
                  </button>

                  <button 
                    className="dashboard-secondary-action"
                    onClick={() => setActiveTab('results')}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                      <LayoutGrid size={18} />
                      <span>RESULTS</span>
                    </div>
                  </button>
                </div>
              )}

              {/* LIVE STATUS component moved out and simplified */}
              {processId && (
                <article className="dashboard-panel">
                  <div className="panel-heading" style={{ marginBottom: '1.5rem' }}>
                    <div>
                      <h2>LIVE STATUS</h2>
                    </div>
                    <span className={`results-status-pill results-status-pill-${status?.status.toLowerCase()}`}>
                      {status?.status ? status.status.charAt(0).toUpperCase() + status.status.slice(1).toLowerCase() : ''}
                    </span>
                  </div>

                  <div className="status-timeline" style={{ maxHeight: '200px', overflowY: 'auto', fontSize: '0.85rem' }}>
                    <div style={{ marginBottom: '1rem', wordBreak: 'break-all' }}>
                      <strong style={{ color: 'var(--text-main)', fontSize: '0.9rem' }}>
                        ID : {file ? file.name : 'Unknown'}_{processId.slice(0, 8)}
                      </strong>
                    </div>
                    {status && (
                      <div className="status-update" style={{ display: 'flex', gap: '12px', padding: '8px 0' }}>
                        <span className="muted">{new Date(status.updated_at).toLocaleTimeString()}</span>
                        <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                          <strong style={{ color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{status.status}</strong>
                        </div>
                      </div>
                    )}
                    
                    <div className="status-logs">
                      {status?.status === 'RUNNING' && <p style={{ margin: '4px 0' }}>{mode === 'optimize' ? 'HEURISTIC SEARCH IN PROGRESS...' : 'CALCULATING OPERATING POINT...'}</p>}
                      {status?.status === 'COMPLETED' && <p style={{ margin: '4px 0', color: 'var(--success)' }}>EXECUTION SUCCESSFUL.</p>}
                      {status?.status === 'FAILED' && <p style={{ margin: '4px 0', color: 'var(--error)' }}>{status.error || 'ANALYSIS FAILED.'}</p>}
                    </div>
                  </div>

                  {(status?.status === 'COMPLETED' || status?.status === 'SUCCESS' || status?.status === 'FAILED') && (
                    <button 
                        className="dashboard-primary-action"
                        style={{ marginTop: '1.5rem' }}
                        onClick={() => setActiveTab('results')}
                      >
                        RESULTS
                      </button>
                    )}
                  </article>
                )}
            </div>

            <div className="dashboard-secondary-column">
              {optimizedResults && (
                <article className="dashboard-panel">
                  <div className="panel-heading">
                    <div>
                      <h2>OPTIMIZED W/L PARAMETERS</h2>
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
                    APPLY OPTIMIZED VALUES
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
