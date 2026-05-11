import React from 'react';
import './FileUploader.css';
import { Upload, X } from 'lucide-react';

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  onRemoveFile: () => void;
  selectedFile: File | null;
}

const FileUploader: React.FC<FileUploaderProps> = ({ onFileSelect, onRemoveFile, selectedFile }) => {
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    const input = document.getElementById('file-input') as HTMLInputElement;
    if (input) {
      input.value = '';
    }
    onRemoveFile();
  };

  return (
    <div className="file-uploader-container">
      <div 
        className={`file-dropzone ${selectedFile ? 'has-file' : ''}`}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <input 
          type="file" 
          id="file-input" 
          hidden 
          onChange={handleChange}
          accept=".py,.spice"
        />
        <div className="file-dropzone-icon">
          {selectedFile ? <Upload size={44} strokeWidth={1.5} /> : <Upload size={44} strokeWidth={1.5} />}
        </div>
        <div className="file-dropzone-content">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px', width: '100%' }}>
            <strong>{selectedFile ? `Uploaded : ${selectedFile.name}` : 'Drop circuit template'}</strong>
            {selectedFile && (
              <button 
                className="remove-file-icon-button" 
                onClick={handleRemove}
                title="Remove file"
              >
                <X size={18} />
              </button>
            )}
          </div>
          <p>{selectedFile ? 'File verified and ready' : 'Supported formats: Python (.py) or SPICE (.spice)'}</p>
        </div>
      </div>
    </div>
  );
};

export default FileUploader;
