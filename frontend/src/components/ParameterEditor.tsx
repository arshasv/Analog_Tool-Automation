import React from 'react';
import './ParameterEditor.css';
import { requiresPositiveValue } from '../utils/spice';

interface Parameter {
  name: string;
  default: any;
  type: string;
  description: string;
}

interface OptimizationParams {
  target: number;
  initial: number;
  epochs: number;
}

interface ParameterEditorProps {
  parameters: Parameter[];
  values: Record<string, any>;
  onChange: (name: string, value: any) => void;
  optimizationParams: Record<string, OptimizationParams>;
  onOptParamChange: (name: string, field: keyof OptimizationParams, value: number) => void;
  mode: 'simulate' | 'optimize';
  disableWL?: boolean;
  errors?: Record<string, string>;
}

const ParameterEditor: React.FC<ParameterEditorProps> = ({ 
  parameters, 
  values, 
  onChange,
  optimizationParams,
  onOptParamChange,
  mode,
  disableWL = false,
  errors = {}
}) => {
  if (parameters.length === 0) {
    return (
      <div className="dashboard-panel">
        <p className="muted">No parameters detected. Ensure the circuit file has introspectable parameters.</p>
      </div>
    );
  }

  // Width and Length are "Free Variables" (starting points)
  const isWLParam = (name: string) => {
    const n = name.toLowerCase();
    return n.startsWith('w') || n.startsWith('l') || n === 'width' || n === 'length';
  };

  return (
    <div className="parameter-layout">
      <div className="parameter-grid">
        {/* Step A: Global Design Targets (Gain, Current) */}
        {mode === 'optimize' && (
          <div className="dashboard-panel parameter-card full-width">
            <div className="panel-heading" style={{ marginBottom: '16px', padding: 0, border: 'none' }}>
              <h2 style={{ fontSize: '1.1rem', color: 'var(--text-main)', letterSpacing: '0.02em' }}>Optimization Targets</h2>
            </div>
            <div className="targets-row">
                <div className="param-input-container">
                  <label>Target Current (I)</label>
                  <input
                    type="text"
                    className={`dashboard-input ${errors['target_current'] ? 'input-error' : ''}`}
                    value={values['target_current'] ?? ''}
                    onChange={(e) => onChange('target_current', e.target.value)}
                    placeholder="e.g. 100u"
                  />
                  {errors['target_current'] && (
                    <div className="input-error-message" style={{ color: 'var(--error)', fontSize: '0.75rem', marginTop: '4px' }}>
                      ⚠️ {errors['target_current']}
                    </div>
                  )}
                </div>
                <div className="param-input-container">
                  <label>Target Gain (dB)</label>
                  <input
                    type="text"
                    className={`dashboard-input ${errors['target_gain'] ? 'input-error' : ''}`}
                    value={values['target_gain'] ?? ''}
                    onChange={(e) => onChange('target_gain', e.target.value)}
                    placeholder="e.g. 60"
                  />
                  {errors['target_gain'] && (
                    <div className="input-error-message" style={{ color: 'var(--error)', fontSize: '0.75rem', marginTop: '4px' }}>
                      ⚠️ {errors['target_gain']}
                    </div>
                  )}
                </div>
              </div>
            </div>
        )}

        {/* Step B: Circuit Parameters Grid */}
        {parameters.filter(p => p.name !== 'process_id').map((param) => (
          <div key={param.name} className="dashboard-panel parameter-card">
            <div className="param-info">
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <strong className="param-name">{param.name}</strong>
                {requiresPositiveValue(param.name) && (
                  <span style={{ fontSize: '0.65rem', fontWeight: 600, color: 'var(--text-secondary)', letterSpacing: '0.05em' }}>
                    (positive only)
                  </span>
                )}
              </div>
              <span className="param-type">{param.type}</span>
            </div>
            
            <div className="param-inputs-row">
              <div className="param-input-container">
                <label>{mode === 'optimize' && isWLParam(param.name) ? 'Initial' : 'Value'}</label>
                <input
                  type="text"
                  className={`dashboard-input ${errors[param.name] ? 'input-error' : ''}`}
                  value={values[param.name] ?? ''}
                  onChange={(e) => onChange(param.name, e.target.value)}
                  disabled={isWLParam(param.name) && disableWL}
                  placeholder={`Ex: ${param.default}`}
                />
                {errors[param.name] && (
                  <div className="input-error-message" style={{ color: 'var(--error)', fontSize: '0.75rem', marginTop: '4px' }}>
                    ⚠️ {errors[param.name]}
                  </div>
                )}
              </div>

              {mode === 'optimize' && !isWLParam(param.name) && (
                <>
                  <div className="param-input-container">
                    <label>Target</label>
                    <input
                      type="text"
                      className={`dashboard-input ${errors[`${param.name}_target`] ? 'input-error' : ''}`}
                      value={optimizationParams[param.name]?.target ?? ''}
                      onChange={(e) => onOptParamChange(param.name, 'target', Number(e.target.value))}
                      placeholder="Ex: 50"
                    />
                    {errors[`${param.name}_target`] && (
                      <div className="input-error-message" style={{ color: 'var(--error)', fontSize: '0.75rem', marginTop: '4px' }}>
                        ⚠️ {errors[`${param.name}_target`]}
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* JSON Preview remains sticky at bottom or separate */}
      {parameters.length > 0 && (
        <div className="dashboard-panel json-preview">
          <span className="muted" style={{ fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.05em' }}>
            JSON PAYLOAD PREVIEW
          </span>
          <pre>{JSON.stringify({ ...values, optimization: mode === 'optimize' ? optimizationParams : undefined }, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default ParameterEditor;
