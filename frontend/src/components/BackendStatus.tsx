import React, { useEffect } from 'react';
import { useBackendHealth } from '../hooks/useBackendHealth';
import './BackendStatus.css';

const BackendStatus: React.FC = () => {
  const { loading, statusText, isError, checkHealth } = useBackendHealth();

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  return (
    <div className={`backend-status-badge ${isError ? 'error' : 'success'}`} onClick={checkHealth}>
      <span className="status-dot" />
      <span className="status-text">{loading ? 'Checking...' : statusText}</span>
    </div>
  );
};

export default BackendStatus;
