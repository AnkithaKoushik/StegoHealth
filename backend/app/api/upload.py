import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, HTTPException
from typing import List
import zipfile
import os
from ..ml.model import ModelHandler

router = APIRouter()

UPLOAD_DIR = Path("storage/uploads")
IMAGES_DIR = Path("storage/images")
RESULTS_DIR = Path("storage/results")

# Ensure directories exist
for dir_path in [UPLOAD_DIR, IMAGES_DIR, RESULTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Initialize model handler
model_handler = ModelHandler()

@router.post("/upload")
async def upload_file(file: UploadFile):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are allowed")
    
    file_path = UPLOAD_DIR / file.filename
    try:
        # Save uploaded file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract ZIP contents
        extract_dir = IMAGES_DIR / file_path.stem
        extract_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Get list of image files
        image_files = []
        for ext in ('*.jpg', '*.jpeg', '*.png'):
            image_files.extend(list(extract_dir.glob(ext)))
        
        if not image_files:
            raise HTTPException(status_code=400, detail="No valid images found in ZIP file")
        
        # Process images
        results = model_handler.process_images(image_files)
        
        # Save results
        result_file = RESULTS_DIR / f"{file_path.stem}_results.json"
        import json
        with result_file.open('w') as f:
            json.dump(results, f)
        
        return {
            "message": "Processing completed successfully",
            "filename": file.filename,
            "images_processed": len(results),
            "results": results
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up uploaded zip
        if file_path.exists():
            file_path.unlink()

from fastapi import APIRouter

# router = APIRouter()

@router.get("/test")
async def test_endpoint():
    return {"message": "Upload endpoint working"}