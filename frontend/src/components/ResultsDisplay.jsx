const ResultsDisplay = ({ images }) => {
    if (!images || images.length === 0) {
      return null;
    }
  
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-semibold mb-4">Processed Images</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {images.map((image, index) => (
            <div 
              key={index}
              className="border rounded-lg p-4 hover:shadow-lg transition-shadow"
            >
              <h3 className="font-medium mb-2">{image.filename}</h3>
              
              {image.status === 'success' ? (
                <div className="space-y-3">
                  {image.feature_visualization && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-1">Feature Map:</p>
                      <img 
                        src={`data:image/png;base64,${image.feature_visualization}`}
                        alt="Feature visualization"
                        className="w-full rounded-lg"
                      />
                    </div>
                  )}
                  
                  <div className="text-sm space-y-1">
                    <p className="text-gray-600">
                      Mean Activation: {image.mean_activation.toFixed(4)}
                    </p>
                    <p className="text-gray-600">
                      Max Activation: {image.max_activation.toFixed(4)}
                    </p>
                    <p className="text-gray-600">
                      Feature Shape: {image.shape?.join(' × ')}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-red-600">
                  Error: {image.error || 'Unknown error occurred'}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };
  
  export default ResultsDisplay;