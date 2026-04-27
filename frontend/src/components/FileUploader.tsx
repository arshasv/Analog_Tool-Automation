import React from 'react';
import './FileUploader.css';

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
}

const FileUploader: React.FC<FileUploaderProps> = ({ onFileSelect, selectedFile }) => {
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
        <div className="file-dropzone-icon">+</div>
        <div>
          <strong>{selectedFile ? selectedFile.name : 'Drag a circuit file here'}</strong>
          <p>{selectedFile ? 'Click to change file' : 'or browse a local template for simulation and optimization'}</p>
        </div>
      </div>
      
      {selectedFile && (
        <div className="selected-file-card">
          <div>
            <span>Selected file</span>
            <strong>{selectedFile.name}</strong>
          </div>
          <div>
            <span>Detected type</span>
            <strong>{selectedFile.name.endsWith('.py') ? 'Python circuit template' : 'SPICE Netlist'}</strong>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
