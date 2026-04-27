import React from 'react';
import './ParameterEditor.css';

interface Parameter {
  name: string;
  default: any;
  type: string;
  description: string;
}

interface ParameterEditorProps {
  parameters: Parameter[];
  values: Record<string, any>;
  onChange: (name: string, value: any) => void;
}

const ParameterEditor: React.FC<ParameterEditorProps> = ({ parameters, values, onChange }) => {
  if (parameters.length === 0) {
    return (
      <div className="parameter-empty">
        <p>No parameters detected. Ensure the circuit file has introspectable parameters.</p>
      </div>
    );
  }

  return (
    <div className="parameter-layout">
      <div className="parameter-table">
        {parameters.map((param) => (
          <div key={param.name} className="parameter-row">
            <div className="param-info">
              <strong>{param.name}</strong>
              <span>{param.description || 'No description'}</span>
            </div>
            <span className="type-pill">{param.type}</span>
            <div className="param-input-container">
              <label>Value</label>
              <input
                type="text"
                value={values[param.name] ?? ''}
                onChange={(e) => onChange(param.name, e.target.value)}
                placeholder={String(param.default)}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="json-preview-card">
        <span>JSON PAYLOAD PREVIEW</span>
        <pre>{JSON.stringify(values, null, 2)}</pre>
      </div>
    </div>
  );
};

export default ParameterEditor;
