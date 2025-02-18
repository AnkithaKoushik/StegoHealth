import { useState } from 'react';
import FileUpload from './components/FileUpload';
import ResultsDisplay from './components/ResultsDisplay';

function App() {
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedImages, setProcessedImages] = useState([]);

  const handleFileUpload = async (file) => {
    try {
      setIsProcessing(true);
      setUploadStatus('Processing...');

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setProcessedImages(data.results || []);
      setUploadStatus(`Successfully processed ${data.images_processed} images`);
    } catch (error) {
      setUploadStatus('Error: ' + error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">
            Image Processing System
          </h1>
          
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

export default App;