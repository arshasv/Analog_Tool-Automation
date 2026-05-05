import React from 'react';
import './FileUploader.css';

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
        <div className="file-dropzone-icon">{selectedFile ? '✓' : '+'}</div>
        <div className="file-dropzone-content">
          <strong>{selectedFile ? `Uploaded : ${selectedFile.name}` : 'Drop circuit template'}</strong>
          <p>{selectedFile ? 'File verified and ready' : 'Supported formats: Python (.py) or SPICE (.spice)'}</p>
        </div>
      </div>
      
      {selectedFile && (
        <button className="remove-file-button" onClick={handleRemove}>
          Remove and replace file
        </button>
      )}
    </div>
  );
};

export default FileUploader;
