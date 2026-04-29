import React from 'react';
import './ParameterEditor.css';

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
}

const ParameterEditor: React.FC<ParameterEditorProps> = ({ 
  parameters, 
  values, 
  onChange,
  optimizationParams,
  onOptParamChange,
  mode
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
      <div className="parameter-list">
        {/* Step A: Global Design Targets (Gain, Current) */}
        {mode === 'optimize' && (
          <div className="dashboard-panel">
            <div className="panel-heading" style={{ marginBottom: '1.5rem' }}>
              <div>
                <span className="panel-eyebrow">Design Goals</span>
                <h2 style={{ fontSize: '1.25rem' }}>Optimization Targets</h2>
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
              <div className="param-input-container">
                <label>Target Current (I)</label>
                <input
                  type="text"
                  className="dashboard-input"
                  value={values['target_current'] ?? ''}
                  onChange={(e) => onChange('target_current', e.target.value)}
                  placeholder="e.g. 100u"
                  style={{ width: '100%' }}
                />
              </div>
              <div className="param-input-container">
                <label>Target Gain (dB)</label>
                <input
                  type="text"
                  className="dashboard-input"
                  value={values['target_gain'] ?? ''}
                  onChange={(e) => onChange('target_gain', e.target.value)}
                  placeholder="e.g. 60"
                  style={{ width: '100%' }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Step B: Circuit Parameters List */}
        {parameters.map((param) => (
          <div key={param.name} className="dashboard-panel parameter-row">
            <div className="param-info">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <strong style={{ fontSize: '1.1rem' }}>{param.name}</strong>
                <span className="type-pill">{param.type}</span>
                {isWLParam(param.name) && (
                  <span className="badge" style={{ background: 'rgba(244, 178, 63, 0.1)', color: 'var(--warning)', borderColor: 'rgba(244, 178, 63, 0.2)' }}>
                    Free Variable
                  </span>
                )}
              </div>
              <span className="muted" style={{ fontSize: '0.9rem', marginTop: '4px', display: 'block' }}>
                {param.description || 'No description provided'}
              </span>
            </div>
            
            <div className="param-inputs" style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', marginTop: '12px' }}>
              <div className="param-input-container">
                <label>{mode === 'optimize' && isWLParam(param.name) ? 'Starting Point' : 'Value'}</label>
                <input
                  type="text"
                  className="dashboard-input"
                  value={values[param.name] ?? ''}
                  onChange={(e) => onChange(param.name, e.target.value)}
                  placeholder={String(param.default)}
                  style={{ width: '120px' }}
                />
              </div>

              {/* Only show target/initial if it's NOT a W/L free variable and we are optimizing */}
              {mode === 'optimize' && !isWLParam(param.name) && (
                <>
                  <div className="param-input-container">
                    <label>Target</label>
                    <input
                      type="text"
                      className="dashboard-input"
                      value={optimizationParams[param.name]?.target ?? ''}
                      onChange={(e) => onOptParamChange(param.name, 'target', e.target.value)}
                      placeholder="Goal"
                      style={{ width: '100px' }}
                    />
                  </div>
                  <div className="param-input-container">
                    <label>Initial</label>
                    <input
                      type="text"
                      className="dashboard-input"
                      value={optimizationParams[param.name]?.initial ?? ''}
                      onChange={(e) => onOptParamChange(param.name, 'initial', e.target.value)}
                      placeholder="Start"
                      style={{ width: '100px' }}
                    />
                  </div>
                </>
              )}
            </div>
          </div>
        ))}
        
        {mode === 'optimize' && (
           <div className="dashboard-panel">
              <div className="param-input-container">
                <label style={{ fontWeight: 600, color: 'var(--accent)' }}>Optimization Epochs</label>
                <p className="muted" style={{ fontSize: '0.8rem', marginBottom: '8px' }}>Total iterations for the search process</p>
                <input
                  type="number"
                  className="dashboard-input"
                  value={values['epochs'] ?? 100}
                  onChange={(e) => onChange('epochs', parseInt(e.target.value))}
                  min={1}
                  max={1000}
                  style={{ width: '100%', maxWidth: '200px' }}
                />
              </div>
           </div>
        )}
      </div>

      <div className="dashboard-panel json-preview">
        <span className="muted" style={{ fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.05em' }}>
          JSON PAYLOAD PREVIEW
        </span>
        <pre>{JSON.stringify({ ...values, optimization: mode === 'optimize' ? optimizationParams : undefined }, null, 2)}</pre>
      </div>
    </div>
  );
};

export default ParameterEditor;
