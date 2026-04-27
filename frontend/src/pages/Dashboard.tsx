import React, { useState, useEffect } from 'react';
import api, { StatusResponse } from '../services/api';
import './Dashboard.css';
import FileUploader from '../components/FileUploader';
import ParameterEditor from '../components/ParameterEditor';
import ResultsViewer from '../components/ResultsViewer';

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
  const [mode, setMode] = useState<'simulate' | 'optimize'>('simulate');
  const [processId, setProcessId] = useState<string | null>(null);
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'workflow' | 'results'>('workflow');

  useEffect(() => {
    if (!processId) {
      return;
    }

    const currentStatus = status?.status?.toLowerCase();
    if (currentStatus === 'completed' || currentStatus === 'success' || currentStatus === 'failed') {
      return;
    }

    const interval = window.setInterval(async () => {
      try {
        const res = await api.getStatus(processId);
        if (res.success && res.data) {
          const nextStatus = res.data;
          setStatus(nextStatus);

          const normalizedNextStatus = nextStatus.status.toLowerCase();
          if (normalizedNextStatus === 'completed' || normalizedNextStatus === 'success') {
            setActiveTab('results');
            window.clearInterval(interval);
          }

          if (normalizedNextStatus === 'failed') {
            window.clearInterval(interval);
          }
        }
      } catch (err) {
        console.error('Polling error', err);
      }
    }, 3000);

    return () => window.clearInterval(interval);
  }, [processId, status?.status]);

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

  const handleParamChange = (name: string, value: any) => {
    setParamValues(prev => ({ ...prev, [name]: value }));
  };

  const handleRun = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.run(file, mode, paramValues);
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

      <div className="dashboard-shell">
        <section className="dashboard-hero">
          <div className="dashboard-hero-copy">
            <span className="dashboard-kicker">AI-Driven Analog Design Platform</span>
            <h1>{activeTab === 'results' ? 'Design Results' : 'Circuit workflow'}</h1>
            <p>
              {activeTab === 'results' 
                ? 'Review performance metrics and download design assets.' 
                : 'Upload, introspect, and execute simulations or optimizations.'}
            </p>
          </div>
          <aside className="dashboard-hero-panel">
            <div className="hero-panel-topline">
              <span className={`status-dot ${processId ? 'status-dot-active' : ''}`} />
              {processId ? `ID: ${processId.substring(0, 12)}...` : 'Ready'}
            </div>
            {status && (
              <div className="hero-panel-meta">
                <div>
                  <span>Status</span>
                  <strong className={`status-text-${status.status.toLowerCase()}`}>{status.status}</strong>
                </div>
                <div>
                  <span>Mode</span>
                  <strong>{mode.toUpperCase()}</strong>
                </div>
              </div>
            )}
          </aside>
        </section>

        {error && <div className="dashboard-error-banner">{error}</div>}

        {activeTab === 'workflow' ? (
          <section className="dashboard-workspace">
            <div className="dashboard-primary-column">
              <article className="dashboard-panel">
                <div className="panel-heading">
                  <div>
                    <span className="panel-eyebrow">1. Intake</span>
                    <h2>Circuit file</h2>
                  </div>
                  <span className="panel-badge">.py / .spice</span>
                </div>
                <FileUploader onFileSelect={handleFileSelect} selectedFile={file} />
              </article>

              {loading && <div className="loading-overlay">Processing...</div>}

              {params.length > 0 && (
                <article className="dashboard-panel">
                  <div className="panel-heading">
                    <div>
                      <span className="panel-eyebrow">2. Parameters</span>
                      <h2>Specifications</h2>
                    </div>
                  </div>
                  <ParameterEditor 
                    parameters={params} 
                    values={paramValues} 
                    onChange={handleParamChange} 
                  />
                </article>
              )}

              <article className="dashboard-panel">
                <div className="panel-heading">
                  <div>
                    <span className="panel-eyebrow">3. Execution</span>
                    <h2>Mode selection</h2>
                  </div>
                </div>
                <div className="mode-toggle-group">
                  <button 
                    className={`mode-toggle-button ${mode === 'simulate' ? 'mode-toggle-button-active' : ''}`}
                    onClick={() => setMode('simulate')}
                  >
                    Simulate
                  </button>
                  <button 
                    className={`mode-toggle-button ${mode === 'optimize' ? 'mode-toggle-button-active' : ''}`}
                    onClick={() => setMode('optimize')}
                  >
                    Optimize
                  </button>
                </div>
                <button 
                  className="dashboard-primary-action" 
                  onClick={handleRun}
                  disabled={!file || loading || (status?.status === 'RUNNING')}
                >
                  {status?.status === 'RUNNING' ? 'Running...' : `Run ${mode}`}
                </button>
              </article>
            </div>

            <div className="dashboard-secondary-column">
              {status && (
                <article className="dashboard-panel dashboard-panel-sticky">
                  <div className="panel-heading">
                    <div>
                      <span className="panel-eyebrow">4. Monitor</span>
                      <h2>Live Status</h2>
                    </div>
                    <span className={`status-pill status-pill-${status.status.toLowerCase()}`}>
                      {status.status}
                    </span>
                  </div>
                  <div className="status-timeline">
                    <div className="status-update">
                      <span>{new Date(status.updated_at).toLocaleTimeString()}</span>
                      <strong>{status.status}</strong>
                      <p>Worker update received.</p>
                    </div>
                  </div>
                  {(status.status === 'COMPLETED' || status.status === 'SUCCESS' || status.status === 'FAILED') && (
                    <button 
                      className="dashboard-primary-action"
                      style={{ marginTop: '1rem' }}
                      onClick={() => setActiveTab('results')}
                    >
                      View Results
                    </button>
                  )}
                </article>
              )}
            </div>
          </section>
        ) : (
          <section className="dashboard-results-view">
             <article className="dashboard-panel">
                <ResultsViewer status={status} />
             </article>
          </section>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
