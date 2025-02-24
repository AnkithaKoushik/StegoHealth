import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import FileUpload from './components/FileUpload';
import ResultsDisplay from './components/ResultsDisplay';
import Login from './components/Login';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider, useAuth } from './context/AuthContext';

function AppContent() {
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedImages, setProcessedImages] = useState([]);
  const { currentUser, logout } = useAuth();

  const handleFileUpload = async (file) => {
    try {
      setIsProcessing(true);
      setUploadStatus('Processing...');

      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('token');
      
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const data = await response.json();
      setProcessedImages(data.results || []);
      setUploadStatus(`Successfully processed ${data.images_processed} images`);
    } catch (error) {
      setUploadStatus('Error: ' + error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="bg-white shadow">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold text-gray-800">
              Image Processing System
            </h1>
            {currentUser && (
              <div className="flex items-center">
                <span className="mr-4 text-gray-600">
                  Welcome, {currentUser.username}
                </span>
                <button
                  onClick={handleLogout}
                  className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <FileUpload onFileUpload={handleFileUpload} />
          </div>

          {isProcessing && (
            <div className="flex justify-center items-center py-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
              <p className="ml-2">Processing images...</p>
            </div>
          )}

          {uploadStatus && !isProcessing && (
            <div className={`mb-6 p-4 rounded-lg text-center ${
              uploadStatus.includes('Error') 
                ? 'bg-red-100 text-red-700' 
                : 'bg-green-100 text-green-700'
            }`}>
              {uploadStatus}
            </div>
          )}

          {processedImages.length > 0 && (
            <ResultsDisplay images={processedImages} />
          )}
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<AppContent />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;