import React, { useState, useRef } from 'react';
import { Upload, X } from 'lucide-react';

const FileUpload = ({ onFileUpload }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragIn = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragOut = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    setError('');

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      validateAndSetFile(files[0]);
    }
  };

  const validateAndSetFile = (file) => {
    if (file.type === 'application/zip' || file.type === 'application/x-zip-compressed') {
      setFile(file);
      setError('');
      onFileUpload(file);
    } else {
      setError('Please upload a ZIP file containing images');
      setFile(null);
    }
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      validateAndSetFile(files[0]);
    }
  };

  const removeFile = (e) => {
    e.stopPropagation();
    setFile(null);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${error ? 'border-red-300 bg-red-50' : ''}`}
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept=".zip"
          className="hidden"
        />
        
        <Upload className={`w-12 h-12 mx-auto mb-4 ${error ? 'text-red-400' : 'text-gray-400'}`} />
        
        <div className="space-y-2">
          <p className={`text-lg font-medium ${error ? 'text-red-600' : 'text-gray-700'}`}>
            {file ? file.name : 'Drop your ZIP file here'}
          </p>
          <p className={`text-sm ${error ? 'text-red-500' : 'text-gray-500'}`}>
            {error || 'or click to browse (ZIP files only)'}
          </p>
        </div>
        
        {file && (
          <div className="mt-4 flex items-center justify-center gap-2 text-sm text-gray-500">
            <span>Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
            <button
              onClick={removeFile}
              className="p-1 hover:bg-gray-100 rounded-full"
              title="Remove file"
            >
              <X className="w-4 h-4 text-gray-500" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload;