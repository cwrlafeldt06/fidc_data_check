import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, FileText } from 'lucide-react';

const FileUpload = ({ 
  onFileSelect, 
  acceptedFile, 
  onFileRemove, 
  label = "Upload CSV File",
  className = "",
  disabled = false 
}) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/csv': ['.csv']
    },
    multiple: false,
    disabled
  });

  return (
    <div className={`space-y-2 ${className}`}>
      <label className="block text-sm font-medium text-gray-700">
        {label}
      </label>
      
      {acceptedFile ? (
        <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-green-600" />
            <span className="text-sm text-green-800">{acceptedFile.name}</span>
            <span className="text-xs text-green-600">
              ({(acceptedFile.size / 1024).toFixed(1)} KB)
            </span>
          </div>
          <button
            onClick={onFileRemove}
            className="text-green-600 hover:text-green-800 transition-colors"
            disabled={disabled}
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ) : (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary-400 bg-primary-50'
              : 'border-gray-300 hover:border-gray-400'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-600">
            {isDragActive
              ? 'Drop the CSV file here...'
              : 'Drag & drop a CSV file here, or click to select'}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Only CSV files are supported
          </p>
        </div>
      )}
    </div>
  );
};

export default FileUpload; 