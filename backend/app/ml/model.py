# backend/app/ml/model.py
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import matplotlib
from PIL import Image
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io
import base64
from pathlib import Path
from typing import List, Dict
import numpy as np

class ModelHandler:
    def __init__(self):
        # Load ResNet-50 and remove classification layer (same as your notebook)
        self.model = models.resnet50(pretrained=True)
        self.model = torch.nn.Sequential(*list(self.model.children())[:-2])
        self.model.eval()

        # Define transformations (same as your notebook)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.Grayscale(num_output_channels=1),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])

    def preprocess_image(self, image_path: Path) -> torch.Tensor:
        """Preprocess a single image for the model"""
        try:
            # Open and convert to grayscale
            image = Image.open(image_path).convert("L")
            
            # Apply transformations
            image = self.transform(image)
            
            # Convert to 3 channels (model expects RGB)
            image = image.repeat(3, 1, 1)
            
            # Add batch dimension
            return image.unsqueeze(0)
        except Exception as e:
            raise Exception(f"Error preprocessing image {image_path}: {str(e)}")

    def get_feature_visualization(self, features: np.ndarray) -> str:
        """Create visualization of feature maps"""
        # Get mean activation across channels
        feature_map = np.mean(features[0], axis=0)
        
        # Create figure
        plt.figure(figsize=(5, 5))
        plt.imshow(feature_map, cmap='viridis')
        plt.colorbar()
        plt.axis('off')
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

    def process_images(self, image_paths: List[Path]) -> List[Dict]:
        results = []
        
        for img_path in image_paths:
            try:
                # Preprocess image
                image_tensor = self.preprocess_image(img_path)
                
                # Extract features
                with torch.no_grad():
                    features = self.model(image_tensor)
                features_np = features.numpy()
                
                # Create feature visualization
                feature_viz = self.get_feature_visualization(features_np)
                
                # Calculate statistics
                results.append({
                    'filename': img_path.name,
                    'status': 'success',
                    'feature_visualization': feature_viz,
                    'mean_activation': float(np.mean(features_np)),
                    'max_activation': float(np.max(features_np)),
                    'shape': list(features_np.shape)
                })
                
            except Exception as e:
                results.append({
                    'filename': img_path.name,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results