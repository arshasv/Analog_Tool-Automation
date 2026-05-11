import React from 'react';
import api, { StatusResponse } from '../services/api';
import './ResultsViewer.css';

interface ResultsViewerProps {
  status: StatusResponse | null;
  onApplyOptimized?: (params: Record<string, any>) => void;
}

type ResultRecord = Record<string, unknown>;

const TERMINAL_STATUSES = new Set(['completed', 'success', 'failed']);

function isRecord(value: unknown): value is ResultRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function formatLabel(value: string): string {
  return value
    .replace(/[_-]+/g, ' ')
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replace(/\s+/g, ' ')
    .trim()
    .toUpperCase();
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) {
    return 'N/A';
  }

  if (typeof value === 'number') {
    if (!Number.isFinite(value)) {
      return String(value);
    }

    if (Math.abs(value) >= 1000 || (Math.abs(value) > 0 && Math.abs(value) < 0.001)) {
      return value.toExponential(3);
    }

    return value.toLocaleString(undefined, { maximumFractionDigits: 4 });
  }

  if (typeof value === 'boolean') {
    return value ? 'Pass' : 'Fail';
  }

  if (Array.isArray(value)) {
    return `${value.length} item${value.length === 1 ? '' : 's'}`;
  }

  if (isRecord(value)) {
    return `${Object.keys(value).length} field${Object.keys(value).length === 1 ? '' : 's'}`;
  }

  return String(value);
}

const ResultsViewer: React.FC<ResultsViewerProps> = ({ status, onApplyOptimized }) => {
  const [showRawResults, setShowRawResults] = React.useState(false);
  const [showFailureDetails, setShowFailureDetails] = React.useState(true);

  if (!status) {
    return (
      <div className="results-viewer results-viewer-placeholder">
        <h3>No run selected yet</h3>
        <p>Start a simulation or optimization to inspect metrics, artifacts, and downloadable results here.</p>
      </div>
    );
  }

  const formatStatusText = (text: string) => {
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
  };

  const formatModeText = (text: string) => {
    return text.toLowerCase() === 'simulate' ? 'Simulate' : 'Optimize';
  };

  const normalizedStatus = status.status.toLowerCase();
  const results = isRecord(status.results) ? status.results : null;
  const modeValue = results?.mode;
  const mode =
    typeof modeValue === 'string'
      ? modeValue
      : typeof status.mode === 'string'
        ? status.mode
        : 'simulate';

  const metricsSource = results?.metrics;
  const metrics = isRecord(metricsSource)
    ? Object.entries(metricsSource)
    : isRecord(status.metrics)
      ? Object.entries(status.metrics)
      : [];

  const checksSource = results?.checks;
  const checks = isRecord(checksSource) ? Object.entries(checksSource) : [];

  const netlistsSource = results?.netlists;
  const netlists = isRecord(netlistsSource) ? Object.entries(netlistsSource) : [];

  const rawOutputSource = results?.raw_output;
  const rawOutput = isRecord(rawOutputSource) ? rawOutputSource : null;

  const plotSource = results?.plots;
  const plots = Array.isArray(plotSource)
    ? plotSource.filter((value): value is string => typeof value === 'string')
    : [];
console.log('Plots:', plots);
  const optimizedParametersSource = results?.optimized_parameters;
  const optimizedParameters = isRecord(optimizedParametersSource)
    ? Object.entries(optimizedParametersSource)
    : [];

  const resultError =
    typeof status.error === 'string' && status.error.trim().length > 0
      ? status.error
      : Array.isArray(rawOutput?.errors) && rawOutput.errors.length > 0
        ? rawOutput.errors.filter((value): value is string => typeof value === 'string').join('\n')
        : null;

  const canDownload = normalizedStatus === 'completed' || normalizedStatus === 'success';
  const hasStructuredResults = results && Object.keys(results).length > 0;

  return (
    <div className="results-viewer">
      <section className="results-header-summary">
        <div className="panel-heading">
          <div>
            <h2>{mode === 'optimize' ? 'OPTIMIZATION RESULTS' : 'SIMULATION RESULTS'}</h2>
          </div>
        </div>

        <div className="results-header-table">
          <div className="results-header-row">
            <span className="label">ID</span>
            <span className="value process-id">: {status.process_id}</span>
          </div>
          
          <div className="results-header-row">
            <span className="label">STATUS</span>
            <div className="value">
              : {normalizedStatus === 'failed' ? (
                <details className="failure-dropdown" open={showFailureDetails} onToggle={(event) => setShowFailureDetails((event.currentTarget as HTMLDetailsElement).open)}>
                  <summary className={`value status-pill ${normalizedStatus}`} aria-label="Failed status and error details">
                    FAILED
                  </summary>
                  <div className="failure-dropdown-body">
                    <strong>Error</strong>
                    <p>{resultError || 'No error details returned by the backend.'}</p>
                  </div>
                </details>
              ) : (
                <span className={`value status-pill ${normalizedStatus}`}>
                  {formatStatusText(status.status)}
                </span>
              )}
            </div>
          </div>

          <div className="results-header-row">
            <span className="label">MODE</span>
            <span className="value">: {formatModeText(mode)}</span>
          </div>

          <div className="results-header-row">
            <span className="label">UPDATED</span>
            <span className="value">: {new Date(status.updated_at).toLocaleString()}</span>
          </div>
        </div>

        {resultError && <div className="error-text" style={{ marginTop: '1rem' }}>{resultError}</div>}

        {canDownload && (
          <div className="download-actions" style={{ marginTop: '1.5rem' }}>
            <a
              className="download-link-btn"
              href={api.getDownloadUrl(status.process_id)}
              target="_blank"
              rel="noreferrer"
            >
              Download Result Bundle
            </a>
          </div>
        )}
      </section>

      {!hasStructuredResults && !TERMINAL_STATUSES.has(normalizedStatus) && (
        <section className="results-viewer-placeholder results-empty-state">
          <h3>Execution in progress</h3>
          <p>The backend has accepted the run. Detailed metrics and artifacts will appear once the job finishes.</p>
        </section>
      )}

      {!hasStructuredResults && TERMINAL_STATUSES.has(normalizedStatus) && !resultError && (
        <section className="results-viewer-placeholder results-empty-state">
          <h3>No structured payload returned</h3>
          <p>The run has finished, but the backend did not attach a results object for this process.</p>
        </section>
      )}

      {metrics.length > 0 && (
        <section className="metrics-summary">
          <div className="metrics-grid">
            {metrics.map(([key, value]) => {
              // Skip redundant "Fail" status strings and specific ignored metrics
              const lowerValue = String(value).toLowerCase();
              const lowerKey = key.toLowerCase();
              
              if (lowerValue === 'fail') return null;
              if (lowerKey === 'gain_db' || lowerKey === 'phase_margin_deg') return null;
              
              return (
                <div key={key} className="metric-item">
                  <span className="metric-label">{formatLabel(key)}</span>
                  <strong className="metric-value">{formatValue(value)}</strong>
                </div>
              );
            })}
            
            {/* Added standard metric-card style for Best Cost and Iterations when in optimize mode */}
            {mode === 'optimize' && results && (
              <>
                {results.best_cost !== undefined && (
                  <div className="metric-item highlight-card">
                    <span className="metric-label">BEST COST</span>
                    <strong className="metric-value" style={{ color: 'var(--accent)' }}>{formatValue(results.best_cost)}</strong>
                  </div>
                )}
                {results.iterations !== undefined && (
                  <div className="metric-item">
                    <span className="metric-label">ITERATIONS</span>
                    <strong className="metric-value">{formatValue(results.iterations)}</strong>
                  </div>
                )}
              </>
            )}
          </div>
        </section>
      )}

      {mode === 'optimize' && (
        <section className="artifact-list">
          <div className="section-header">
            <h2>OPTIMIZED W/L PARAMETERS</h2>
          </div>
          
          {optimizedParameters.length > 0 && (
            <>
              <div className="results-key-value-grid optimized-wl-grid">
                {optimizedParameters.map(([key, value]) => (
                  <div key={key} className="results-key-value-card wl-card">
                    <span className="wl-label">{formatLabel(key)}</span>
                    <strong className="wl-value">{formatValue(value)}</strong>
                  </div>
                ))}
              </div>
              
              {onApplyOptimized && (
                <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'flex-start' }}>
                  <button 
                    className="dashboard-primary-action"
                    style={{ 
                      padding: '12px 24px', 
                      fontSize: '0.875rem', 
                      margin: 0,
                      width: 'auto',
                      minWidth: '200px'
                    }}
                    onClick={() => onApplyOptimized(isRecord(optimizedParametersSource) ? (optimizedParametersSource as Record<string, any>) : {})}
                  >
                    APPLY OPTIMIZED VALUES
                  </button>
                </div>
              )}
            </>
          )}
        </section>
      )}

      {checks.length > 0 && (
        <section className="artifact-list">
          {checks.map(([key, value]) => {
            const lowerValue = String(value).toLowerCase();
            const lowerKey = key.toLowerCase();
            
            if (lowerValue === 'fail') return null;
            if (lowerKey === 'gain_db' || lowerKey === 'phase_margin_deg') return null;
            
            return (
              <div key={key} className="artifact">
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>{formatLabel(key)}</span>
                <strong>{formatValue(value)}</strong>
              </div>
            );
          })}
        </section>
      )}

      {hasStructuredResults && (
        <section className="raw-results" style={{ marginTop: '24px' }}>
          <button 
            className="dashboard-secondary-action"
            style={{ 
              width: '100%', 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              padding: '12px 16px',
              fontSize: '0.8rem',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              background: 'var(--status-pill-bg)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              color: 'var(--text-main)',
              cursor: 'pointer'
            }}
            onClick={() => setShowRawResults(!showRawResults)}
          >
            <span>Raw Results Payload</span>
            <span>{showRawResults ? '▲' : '▼'}</span>
          </button>
          
          {showRawResults && (
            <pre style={{ 
              marginTop: '12px', 
              background: 'var(--background)', 
              padding: '16px', 
              borderRadius: '8px', 
              border: '1px solid var(--border)',
              fontSize: '0.8rem',
              overflow: 'auto',
              maxHeight: '400px'
            }}>
              {JSON.stringify(results, null, 2)}
            </pre>
          )}
        </section>
      )}
    </div>
  );
};

export default ResultsViewer;
