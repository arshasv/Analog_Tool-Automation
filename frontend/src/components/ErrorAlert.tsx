import React from 'react';
import './ErrorAlert.css';

interface ErrorAlertProps {
  message: string;
  onDismiss?: () => void;
}

const ErrorAlert: React.FC<ErrorAlertProps> = ({ message, onDismiss }) => {
  if (!message) return null;

  return (
    <div className="error-alert">
      <div className="error-alert-content">
        <span className="error-alert-icon">⚠️</span>
        <span className="error-alert-message">{message}</span>
      </div>
      {onDismiss && (
        <button className="error-alert-dismiss" onClick={onDismiss} aria-label="Dismiss error">
          &times;
        </button>
      )}
    </div>
  );
};

export default ErrorAlert;
