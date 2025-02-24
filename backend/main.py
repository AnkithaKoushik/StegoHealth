from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload
from app.api.auth import router as auth_router, get_current_user

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

# Include upload router with authentication
app.include_router(
    upload.router, 
    prefix="/api", 
    tags=["upload"],
    dependencies=[Depends(get_current_user)]  # Protect all upload routes
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)