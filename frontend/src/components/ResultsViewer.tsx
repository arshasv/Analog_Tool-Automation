import React from 'react';
import api, { StatusResponse } from '../services/api';
import './ResultsViewer.css';

interface ResultsViewerProps {
  status: StatusResponse | null;
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
    .replace(/\b\w/g, (char) => char.toUpperCase());
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

const ResultsViewer: React.FC<ResultsViewerProps> = ({ status }) => {
  if (!status) {
    return (
      <div className="results-viewer results-viewer-placeholder">
        <h3>No run selected yet</h3>
        <p>Start a simulation or optimization to inspect metrics, artifacts, and downloadable results here.</p>
      </div>
    );
  }

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
        <div className="results-summary-topline">
          <div>
            <span className="panel-eyebrow">Run Snapshot</span>
            <h2>{mode === 'optimize' ? 'Optimization results' : 'Simulation results'}</h2>
          </div>
          <span className={`results-status-pill results-status-pill-${normalizedStatus}`}>
            {status.status}
          </span>
        </div>

        <div className="results-overview-grid">
          <div className="overview-card">
            <span>Process</span>
            <strong>{status.process_id}</strong>
          </div>
          <div className="overview-card">
            <span>Mode</span>
            <strong>{formatLabel(mode)}</strong>
          </div>
          <div className="overview-card">
            <span>Progress</span>
            <strong>{typeof status.progress === 'number' ? `${status.progress}%` : 'N/A'}</strong>
          </div>
          <div className="overview-card">
            <span>Updated</span>
            <strong>{new Date(status.updated_at).toLocaleString()}</strong>
          </div>
        </div>

        {resultError && <div className="error-text">{resultError}</div>}

        {canDownload && (
          <div className="download-actions">
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
            <h4>Performance Metrics</h4>
            <span>{metrics.length} captured</span>
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
          <div className="artifact-head">
            <h3>Optimization Summary</h3>
            <span>{historyLength > 0 ? `${historyLength} history points` : 'Summary'}</span>
          </div>
          <div className="artifact">
            <span>Best Cost</span>
            <span>{formatValue(results?.best_cost)}</span>
          </div>
          <div className="artifact">
            <span>Iterations</span>
            <span>{formatValue(results?.iterations)}</span>
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
          <div className="artifact-head">
            <h3>Checks</h3>
            <span>Constraint review</span>
          </div>
          {checks.map(([key, value]) => (
            <div key={key} className="artifact">
              <span>{formatLabel(key)}</span>
              <span>{formatValue(value)}</span>
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
          <div className="artifact-head">
            <h3>Artifacts</h3>
            <span>{netlists.length + plots.length} available</span>
          </div>
          {netlists.map(([key, value]) => (
            <div key={key} className="artifact">
              <span>{formatLabel(key)}</span>
              <span>{typeof value === 'string' ? value.split('/').pop() : formatValue(value)}</span>
            </div>
          ))}
          {plots.map((plot, index) => (
            <div key={`${plot}-artifact-${index}`} className="artifact">
              <span>{`Plot ${index + 1}`}</span>
              <span>{plot.split('/').pop() ?? plot}</span>
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
