## Research Paper Podcast System

This project implements a multi-agent system that processes research papers from PDFs, DOIs, or URLs, generates summaries, classifies topics, and produces audio podcasts using text-to-speech technology. The system supports both a FastAPI-based web service and a command-line interface (CLI).

## Table of Contents
- [Setup Instructions](#setup-instructions)
- [System Architecture](#system-architecture)
- [Multi-Agent Design and Coordination](#multi-agent-design-and-coordination)
- [Paper Processing Methodology](#paper-processing-methodology)
- [Audio Generation Implementation](#audio-generation-implementation)
- [Limitations and Future Improvements](#limitations-and-future-improvements)
- [License](#license)

## 📸 Preview

📄 PDF Upload
<p align="center"> <img src="Screenshot 2025-08-01 012733.png" width="700" alt="PDF Upload UI Preview"/> </p>
🔗 DOI Input
<p align="center"> <img src="Screenshot 2025-08-01 012917.png" width="700" alt="DOI Input UI Preview"/> </p>
🌐 URL Input
<p align="center"> <img src="Screenshot 2025-08-01 013107.png" width="700" alt="URL Input UI Preview"/> </p>


## Setup Instructions

### Prerequisites
- Python 3.8+
- Git
- A modern web browser (for API interaction with a React frontend, if used)

### Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/research-paper-podcast-system.git
   cd research-paper-podcast-system
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   **requirements.txt** (create this file in the project root):
   ```text
   requests
   beautifulsoup4
   PyPDF2
   transformers
   gTTS
   fastapi
   uvicorn
   ```

4. **Set up output directory**:
   The system creates an `outputs` directory for audio files. Ensure write permissions in the project directory.

5. **Run the system**:
   - **As an API**:
     ```bash
     python main.py api
     ```
     The API runs at `http://localhost:8000`. Use a frontend (e.g., React at `http://localhost:3000`) or tools like Postman to interact with the `/process` endpoint.
   - **As a CLI**:
     ```bash
     python main.py
     ```
     Follow the interactive prompts to input PDFs, DOIs, URLs, and topics.

### Optional Frontend
For API interaction via a web interface, set up a React frontend (not included):
- Ensure CORS is configured for your frontend URL (default: `http://localhost:3000`).
- Update `allow_origins` in `main.py` if your frontend uses a different port.

## System Architecture

The system is a modular pipeline with the following components:
- **Input Processing**: Extracts text from PDFs, DOIs, or URLs.
- **Text Analysis**: Uses NLP for summarization and topic classification.
- **Audio Generation**: Converts summaries to audio files.
- **Interface**: Provides FastAPI endpoints for web access and a CLI for local use.
- **Output Management**: Stores audio files and metadata in the `outputs` directory.

Built in Python using FastAPI, the system relies on libraries like PyPDF2, BeautifulSoup, Transformers, and gTTS. It supports synchronous CLI workflows and asynchronous API requests.

## Multi-Agent Design and Coordination

The system uses a multi-agent approach, with each agent handling a specific task, coordinated by the `run_system` function:

### PDF Extraction Agent
- Function: `extract_text_from_pdf`
- Extracts text from PDFs using PyPDF2.
- Concatenates text from all pages for analysis.

### DOI Metadata Agent
- Function: `resolve_doi`
- Fetches metadata (title, authors, journal, abstract) from the Crossref API.
- Formats metadata for summarization.

### URL Content Agent
- Function: `fetch_url_text`
- Scrapes paragraph text from URLs using BeautifulSoup.

### Topic Classification Agent
- Function: `classify_topic`
- Assigns topics based on keyword frequency in summaries.
- Uses user-provided topics or defaults to "Unspecified."

### Summary Generation Agent
- Function: `generate_summary`
- Summarizes text using the DistilBART model from Transformers.
- Processes input in paragraphs for concise output.

### Cross-Paper Synthesis Agent
- Function: `synthesize_across_papers`
- Combines summaries from multiple papers into a cohesive final summary.
- Reuses the summarization pipeline.

### Audio Synthesis Agent
- Function: `generate_audio`
- Converts summaries to MP3 audio using gTTS.
- Saves files to the `outputs` directory.

### Coordination
- The `run_system` function orchestrates agents, processing inputs and passing outputs between them.
- Results are aggregated into a JSON response with citations and a synthesized summary.

## Paper Processing Methodology

The system processes papers through these steps:
1. **Input Collection**:
   - PDFs: Uploaded via API or specified via CLI.
   - DOIs: Resolved via Crossref API for metadata.
   - URLs: Scraped for text content.

2. **Text Extraction**:
   - PDFs: PyPDF2 extracts page text.
   - DOIs: Metadata is formatted as text.
   - URLs: BeautifulSoup extracts paragraphs.

3. **Summarization**:
   - Text is split into paragraphs (>100 characters).
   - DistilBART generates summaries, combined into a single output.
   - Errors return "Summary unavailable."

4. **Topic Classification**:
   - Summaries are analyzed for user-provided topic keywords.
   - The most frequent topic is assigned.

5. **Cross-Paper Synthesis**:
   - Summaries are combined and re-summarized for a cohesive overview.

6. **Output Generation**:
   - Summaries are converted to audio.
   - Citations (source, topic, audio path) are compiled.
   - A final synthesized audio summary is produced.

## Audio Generation Implementation

The `generate_audio` function handles audio generation:
- **Library**: gTTS (Google Text-to-Speech) converts text to MP3.
- **Process**:
  - Takes a summary and filename as input.
  - Generates an MP3 file in English, saved to the `outputs` directory.
  - Filenames are derived from PDF names, DOI slugs, or truncated URLs.
- **API Access**: The `/audio/{filename}` endpoint serves MP3 files with `audio/mpeg` media type.
- **Error Handling**: Returns an error if the audio file is not found.

## Limitations and Future Improvements

### Limitations
- **NLP Model**: DistilBART may struggle with technical texts, producing suboptimal summaries.
- **DOI Resolution**: Limited to Crossref API, which may miss some DOIs or metadata.
- **URL Scraping**: Basic parsing misses structured content or dynamic pages.
- **Audio Quality**: gTTS provides basic text-to-speech; intonation and expressiveness are limited.



## Future Improvements

This document outlines planned enhancements for the Research Paper Podcast System to improve functionality, performance, and user experience.

### Advanced NLP Models
Integrate larger, more powerful natural language processing models such as BART-large or T5 to enhance summarization quality. These models can better handle complex and domain-specific texts, provided sufficient computational resources are available.

### Enhanced DOI Support
Expand DOI resolution by incorporating fallback APIs like PubMed or Semantic Scholar. This will ensure broader coverage and improve retrieval of metadata for papers not available through the Crossref API.

### Improved URL Parsing
Adopt advanced web scraping tools, such as Scrapy, to handle dynamic content and structured data (e.g., tables, figures) on web pages. This will improve the accuracy and completeness of text extracted from URLs.

### Audio Enhancements
Explore alternative text-to-speech solutions like ElevenLabs or AWS Polly to produce more natural-sounding audio with improved intonation and expressiveness, enhancing the podcast experience.

### Parallel Processing
Implement multiprocessing or asynchronous task execution to optimize performance when processing large numbers of papers. This will reduce processing time and improve scalability.

### Frontend Integration
Develop a dedicated React-based frontend to provide a seamless, user-friendly interface for interacting with the API, streamlining the process of uploading papers and accessing results.

### Error Recovery
Introduce robust error-handling mechanisms, including retry logic for failed API calls or summarization tasks and alternative summarization methods to ensure system reliability.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
