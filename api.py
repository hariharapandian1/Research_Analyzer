"""
API Server for Research Paper Podcast System
Connects frontend and backend with clean REST API endpoints
"""

import os
import json
import tempfile
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn

# Import the backend processing function
from main import run_system

# Create FastAPI app
app = FastAPI(
    title="Research Paper Podcast System API",
    description="AI-powered system that transforms research papers into audio podcasts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Research Paper Podcast System API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/",
            "process": "/process",
            "audio": "/audio/{filename}",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "Research Paper Podcast System",
        "backend": "operational",
        "output_directory": OUTPUT_DIR,
        "output_directory_exists": os.path.exists(OUTPUT_DIR)
    }

@app.post("/process")
async def process_papers(
    pdf_files: Optional[List[UploadFile]] = File(None),
    data: str = Form(...)
):
    """
    Process research papers and generate audio summaries
    
    Args:
        pdf_files: List of uploaded PDF files
        data: JSON string containing doi_list, urls, topic_list
    
    Returns:
        JSON response with synthesis and citations
    """
    try:
        # Parse the JSON data
        try:
            json_data = json.loads(data)
            doi_list = json_data.get("doi_list", [])
            urls = json_data.get("urls", [])
            topic_list = json_data.get("topic_list", [])
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON data")
        
        # Handle PDF files
        pdf_paths = []
        if pdf_files:
            for pdf_file in pdf_files:
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, 
                    suffix=".pdf",
                    dir=OUTPUT_DIR
                )
                try:
                    # Write uploaded file content
                    content = await pdf_file.read()
                    temp_file.write(content)
                    temp_file.close()
                    pdf_paths.append(temp_file.name)
                except Exception as e:
                    # Clean up on error
                    if os.path.exists(temp_file.name):
                        os.unlink(temp_file.name)
                    raise HTTPException(status_code=500, detail=f"Error saving PDF: {str(e)}")
        
        # Validate inputs
        if not pdf_paths and not doi_list and not urls:
            raise HTTPException(
                status_code=400, 
                detail="At least one input type (PDFs, DOIs, or URLs) is required"
            )
        
        print(f"Processing request:")
        print(f"  PDFs: {len(pdf_paths)} files")
        print(f"  DOIs: {len(doi_list)} entries")
        print(f"  URLs: {len(urls)} entries")
        print(f"  Topics: {len(topic_list)} entries")
        
        # Call the backend processing function
        result = run_system(
            pdf_files=pdf_paths,
            doi_list=doi_list,
            urls=urls,
            topic_list=topic_list
        )
        
        # Clean up temporary PDF files
        for pdf_path in pdf_paths:
            try:
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
            except Exception as e:
                print(f"Warning: Could not delete temporary file {pdf_path}: {e}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing papers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """
    Serve generated audio files
    
    Args:
        filename: Name of the audio file to retrieve
    
    Returns:
        Audio file response
    """
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename
    )

@app.get("/files")
async def list_audio_files():
    """List all available audio files"""
    try:
        files = []
        if os.path.exists(OUTPUT_DIR):
            for filename in os.listdir(OUTPUT_DIR):
                if filename.endswith(('.mp3', '.wav', '.m4a')):
                    file_path = os.path.join(OUTPUT_DIR, filename)
                    file_size = os.path.getsize(file_path)
                    files.append({
                        "filename": filename,
                        "size": file_size,
                        "size_mb": round(file_size / (1024 * 1024), 2)
                    })
        
        return {
            "audio_files": files,
            "total_files": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@app.delete("/files/{filename}")
async def delete_audio_file(filename: str):
    """Delete a specific audio file"""
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        os.remove(file_path)
        return {"message": f"File {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@app.delete("/files")
async def delete_all_audio_files():
    """Delete all audio files"""
    try:
        deleted_count = 0
        if os.path.exists(OUTPUT_DIR):
            for filename in os.listdir(OUTPUT_DIR):
                if filename.endswith(('.mp3', '.wav', '.m4a')):
                    file_path = os.path.join(OUTPUT_DIR, filename)
                    os.remove(file_path)
                    deleted_count += 1
        
        return {
            "message": f"Deleted {deleted_count} audio files",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting files: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Research Paper Podcast System API Server...")
    print("📚 API Documentation available at: http://localhost:8000/docs")
    print("🔗 Frontend should connect to: http://localhost:8000")
    print("🎧 Audio files will be stored in: outputs/")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 