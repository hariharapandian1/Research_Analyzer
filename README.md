# 🎧 Research Paper Podcast System

A complete AI-powered system that transforms research papers into engaging audio podcasts using cutting-edge NLP and text-to-speech technology.

## ✨ Features

### 🧠 AI-Powered Processing
- **PDF Text Extraction**: Advanced PyPDF2 processing for complex layouts
- **DOI Metadata Fetching**: Automatic CrossRef API integration
- **URL Content Scraping**: BeautifulSoup-based web content extraction
- **Topic Classification**: Intelligent categorization system
- **AI Summarization**: State-of-the-art DistilBART model
- **Cross-Paper Synthesis**: Multi-document analysis and insights

### 🎧 Audio Generation
- **High-Quality TTS**: Google Text-to-Speech integration
- **Multiple Formats**: Individual summaries and cross-paper synthesis
- **Custom Audio Players**: Built-in controls with progress tracking
- **File Management**: Automatic cleanup and organization

### 🌐 Multiple Interface Options
- **REST API**: Clean FastAPI endpoints for integration
- **Gradio Interface**: User-friendly web interface
- **React Frontend**: Modern, responsive web application

## 🚀 Quick Start

### Option 1: API Server (Recommended)

1. **Start the API Server**:
```bash
python api.py
```
- API runs on: `http://localhost:8000`
- Documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

2. **Use the API**:
```bash
# Test the API
curl http://localhost:8000/

# Process papers via API
curl -X POST "http://localhost:8000/process" \
  -F "pdf_files=@paper1.pdf" \
  -F "data={\"doi_list\":[\"10.1016/j.cell.2023.01.001\"],\"urls\":[],\"topic_list\":[\"biology\"]}"
```

### Option 2: Gradio Interface

1. **Install Gradio** (if not already installed):
```bash
pip install gradio
```

2. **Start the Gradio Interface**:
```bash
python gradio_interface.py
```
- Interface runs on: `http://localhost:7860`
- No additional setup required

### Option 3: React Frontend

1. **Start the API Server** (from Option 1)

2. **Start the React Frontend**:
```bash
cd research-podcast-frontend
npm start
```
- Frontend runs on: `http://localhost:3000`

## 📁 Project Structure

```
research-paper-podcast-system/
├── main.py                    # Core processing functions
├── api.py                     # FastAPI server
├── gradio_interface.py        # Gradio web interface
├── research-podcast-frontend/ # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API communication
│   │   └── types/            # TypeScript definitions
│   └── package.json
├── outputs/                   # Generated audio files
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🔗 API Endpoints

### Core Endpoints
- `GET /` - Health check and API info
- `GET /health` - Detailed health status
- `POST /process` - Process papers and generate audio
- `GET /audio/{filename}` - Retrieve audio files

### File Management
- `GET /files` - List all audio files
- `DELETE /files/{filename}` - Delete specific audio file
- `DELETE /files` - Delete all audio files

### Request Format
```json
{
  "pdf_files": ["file1.pdf", "file2.pdf"],
  "doi_list": ["10.1016/j.cell.2023.01.001"],
  "urls": ["https://arxiv.org/abs/2301.12345"],
  "topic_list": ["machine learning", "biology"]
}
```

### Response Format
```json
{
  "synthesis": "Cross-paper synthesis text...",
  "synthesis_audio": "synthesis_audio.mp3",
  "citations": [
    {
      "source": "paper1.pdf",
      "topic": "machine learning",
      "audio": "paper1_summary.mp3"
    }
  ]
}
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 16+ (for React frontend)
- Internet connection (for DOI fetching and TTS)

### Python Dependencies
```bash
pip install -r requirements.txt
```

### React Dependencies
```bash
cd research-podcast-frontend
npm install
```

## 🎯 Usage Examples

### Using the API
```python
import requests

# Process papers via API
files = {'pdf_files': open('paper.pdf', 'rb')}
data = {
    'data': '{"doi_list":["10.1016/j.cell.2023.01.001"],"urls":[],"topic_list":["biology"]}'
}

response = requests.post('http://localhost:8000/process', files=files, data=data)
result = response.json()

print(f"Synthesis: {result['synthesis']}")
print(f"Audio: {result['synthesis_audio']}")
```

### Using the Gradio Interface
1. Open `http://localhost:7860`
2. Upload PDF files or enter DOIs/URLs
3. Add optional topics for classification
4. Click "Generate Podcast"
5. View results and download audio

### Using the React Frontend
1. Open `http://localhost:3000`
2. Explore the landing page
3. Click "Start Processing"
4. Upload files and configure options
5. Monitor progress and listen to results

## 🔧 Configuration

### Environment Variables
- `REACT_APP_API_URL`: Backend URL (default: `http://localhost:8000`)

### API Configuration
- **Port**: 8000 (configurable in api.py)
- **CORS**: Enabled for localhost:3000
- **Timeout**: 5 minutes for processing requests
- **Output Directory**: `outputs/` (auto-created)

### Gradio Configuration
- **Port**: 7860 (configurable in gradio_interface.py)
- **Theme**: Soft theme with custom styling
- **File Types**: PDF only for uploads

## 📊 Performance

### Processing Times
- **PDF Processing**: ~30 seconds per paper
- **DOI Fetching**: ~10 seconds per DOI
- **URL Scraping**: ~15 seconds per URL
- **AI Summarization**: ~60 seconds per paper
- **Audio Generation**: ~30 seconds per summary

### Resource Requirements
- **Memory**: 2-4 GB RAM recommended
- **Storage**: 100MB+ for audio files
- **CPU**: Multi-core recommended for parallel processing

## 🎧 Audio Features

### Supported Formats
- **Input**: PDF, DOI, URL
- **Output**: MP3 audio files
- **Quality**: High-quality TTS with natural speech

### Audio Management
- **Automatic Cleanup**: Temporary files removed after processing
- **File Organization**: Structured output directory
- **Streaming**: Efficient audio file serving
- **Download**: Direct file access via API

## 🔮 Advanced Features

### Batch Processing
- Multiple PDF uploads
- Mixed input types (PDFs + DOIs + URLs)
- Parallel processing where possible

### Error Handling
- Graceful failure recovery
- Detailed error messages
- Input validation
- File cleanup on errors

### Monitoring
- Real-time progress tracking
- Processing status updates
- Health check endpoints
- File management utilities

## 🚀 Deployment

### Production API Server
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Production React Build
```bash
cd research-podcast-frontend
npm run build
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "api.py"]
```

## 🧪 Testing

### API Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test file listing
curl http://localhost:8000/files

# Test processing (with sample data)
curl -X POST "http://localhost:8000/process" \
  -F "data={\"doi_list\":[\"10.1016/j.cell.2023.01.001\"]}"
```

### Frontend Testing
```bash
# React frontend
cd research-podcast-frontend
npm test

# Gradio interface
python -m pytest tests/
```

## 🔒 Security Considerations

### API Security
- Input validation and sanitization
- File type restrictions
- Rate limiting (can be added)
- CORS configuration
- Error message sanitization

### File Security
- Temporary file cleanup
- Secure file handling
- Path traversal prevention
- File size limits

## 📈 Monitoring and Logging

### Logging
- Processing progress logs
- Error tracking
- Performance metrics
- File operation logs

### Health Monitoring
- API health checks
- Backend service status
- File system monitoring
- Resource usage tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent web framework
- **Gradio** for the user-friendly interface
- **Transformers** for the AI models
- **Google TTS** for audio generation
- **CrossRef** for DOI metadata

---

**🎧 Research Paper Podcast System** - Making research accessible, one audio summary at a time!

*Built with ❤️ using FastAPI, React, Gradio, and cutting-edge AI technology.* 