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

function isRenderablePlotSource(value: string): boolean {
  return (
    value.startsWith('data:image/') ||
    value.startsWith('blob:') ||
    value.startsWith('http://') ||
    value.startsWith('https://') ||
    value.startsWith('/')
  );
}

const ResultsViewer: React.FC<ResultsViewerProps> = ({ status, onApplyOptimized }) => {
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

  const historySource = results?.history;
  const historyLength = Array.isArray(historySource) ? historySource.length : 0;

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
            <span className="panel-eyebrow">RUN SNAPSHOT</span>
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
              : <span className={`value status-pill ${normalizedStatus}`}>
                {formatStatusText(status.status)}
              </span>
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
          <div className="section-header">
            <h4>PERFORMANCE METRICS</h4>
          </div>
          <div className="metrics-grid">
            {metrics.map(([key, value]) => (
              <div key={key} className="metric-item">
                <span className="metric-label">{formatLabel(key)}</span>
                <strong className="metric-value">{formatValue(value)}</strong>
              </div>
            ))}
          </div>
        </section>
      )}

      {mode === 'optimize' && (
        <section className="artifact-list">
          <div className="section-header">
            <h4>OPTIMIZATION SUMMARY</h4>
            <div style={{ display: 'flex', gap: '8px' }}>
              {optimizedParameters.length > 0 && onApplyOptimized && (
                <button 
                  className="dashboard-primary-action"
                  style={{ 
                    padding: '4px 12px', 
                    fontSize: '0.75rem', 
                    margin: 0,
                    height: 'auto',
                    background: 'var(--accent)',
                    color: '#FFFFFF'
                  }}
                  onClick={() => onApplyOptimized(isRecord(optimizedParametersSource) ? (optimizedParametersSource as Record<string, any>) : {})}
                >
                  APPLY & SIMULATE
                </button>
              )}
            </div>
          </div>
          <div className="artifact">
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>BEST COST</span>
            <strong style={{ color: 'var(--accent)' }}>{formatValue(results?.best_cost)}</strong>
          </div>
          <div className="artifact">
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>ITERATIONS</span>
            <strong>{formatValue(results?.iterations)}</strong>
          </div>
          {optimizedParameters.length > 0 && (
            <div className="results-key-value-grid">
              {optimizedParameters.map(([key, value]) => (
                <div key={key} className="results-key-value-card">
                  <span>{formatLabel(key)}</span>
                  <strong>{formatValue(value)}</strong>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {checks.length > 0 && (
        <section className="artifact-list">
          <div className="section-header">
            <h4>CHECKS</h4>
          </div>
          {checks.map(([key, value]) => (
            <div key={key} className="artifact">
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>{formatLabel(key)}</span>
              <strong>{formatValue(value)}</strong>
            </div>
          ))}
        </section>
      )}

      {/* {plots.length > 0 && (
        <section className="plots-section">
          <div className="section-header">
            <h4>Plots</h4>
            <span>{plots.length} asset{plots.length === 1 ? '' : 's'}</span>
          </div>
          <div className="plots-gallery">
            {plots.map((plot, index) => (
              <div key={`${plot}-${index}`} className="plot-container">
               
                {isRenderablePlotSource(plot) ? (
                  <img className="result-plot" src={plot} alt={`Result plot ${index + 1}`} />
                ) : (
                  <div className="plot-unavailable">
                    <strong>Preview unavailable</strong>
                    <p>The backend returned a filesystem path, so this plot is available in the download bundle.</p>
                  </div>
                )}
                <p className="plot-caption">{plot.split('/').pop() ?? `Plot ${index + 1}`}</p>
              </div>
            ))}
          </div>
        </section>
      )} */}

      {(netlists.length > 0 || plots.length > 0) && (
        <section className="artifact-list">
          <div className="section-header">
            <h4>ARTIFACTS</h4>
          </div>
          {netlists.map(([key, value]) => (
            <div key={key} className="artifact">
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>{formatLabel(key)}</span>
              <strong>SPICE NETLIST</strong>
            </div>
          ))}
          {plots.map((plot, index) => (
            <div key={`${plot}-artifact-${index}`} className="artifact">
              <span>{`PLOT ${index + 1}`}</span>
              <strong>{plot.split('/').pop() ?? plot}</strong>
            </div>
          ))}
        </section>
      )}

      {hasStructuredResults && (
        <section className="raw-results">
          <div className="section-header">
            <h4>Raw Results</h4>
            <span>Backend payload</span>
          </div>
          <pre>{JSON.stringify(results, null, 2)}</pre>
        </section>
      )}
    </div>
  );
};

export default ResultsViewer;
