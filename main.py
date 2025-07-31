# === MULTI-AGENT SYSTEM FOR RESEARCH PAPER PODCASTS ===

# --- Imports ---
import os
import requests
import json
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from transformers import pipeline
from gtts import gTTS
from typing import List
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn

# --- Constants ---
SUMMARY_PIPELINE = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- FastAPI App ---
app = FastAPI(title="Research Paper Podcast System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================== #
#   1. PDF TEXT EXTRACTION
# ========================== #
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    return text

# ========================== #
#   2. DOI Metadata Fetch
# ========================== #
def resolve_doi(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["message"]
        return {
            "title": data.get("title", [""])[0],
            "authors": [a.get("family") for a in data.get("author", [])],
            "journal": data.get("container-title", [""])[0],
            "date": data.get("published-print", {}).get("date-parts", [[None]])[0][0],
            "link": data.get("URL"),
            "abstract": data.get("abstract", "")
        }
    return {"error": "DOI not found"}

# ========================== #
#   3. URL Content Fetch
# ========================== #
def fetch_url_text(url):
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        paragraphs = soup.find_all("p")
        content = "\n".join(p.get_text() for p in paragraphs)
        return content
    except Exception as e:
        print(f"❌ Failed to fetch URL {url}: {e}")
        return ""

# ========================== #
#   4. TOPIC CLASSIFICATION
# ========================== #
def classify_topic(text: str, topics: List[str]):
    return max(topics, key=lambda topic: text.lower().count(topic.lower())) if topics else "Unspecified"

# ========================== #
#   5. SUMMARY GENERATION
# ========================== #
def generate_summary(text: str):
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 100]
    try:
        summaries = SUMMARY_PIPELINE(paragraphs, truncation=True, max_length=200, min_length=50)
        return " ".join([s["summary_text"] for s in summaries])
    except Exception as e:
        print("⚠️ Summarization failed:", e)
        return "Summary unavailable."

# ========================== #
#   6. CROSS-PAPER SYNTHESIS
# ========================== #
def synthesize_across_papers(summaries: List[str]):
    return generate_summary(" ".join(summaries))

# ========================== #
#   7. AUDIO SYNTHESIS
# ========================== #
def generate_audio(text: str, filename: str):
    tts = gTTS(text=text, lang='en')
    output_path = os.path.join(OUTPUT_DIR, f"{filename}.mp3")
    tts.save(output_path)
    return output_path

# ========================== #
#   8. SYSTEM RUNNER
# ========================== #
def run_system(pdf_files=[], topic_list=[], doi_list=[], urls=[]):
    all_summaries = []
    citations = []

    # --- Process PDFs ---
    for pdf_path in pdf_files:
        print(f"📄 Processing PDF: {pdf_path}")
        raw_text = extract_text_from_pdf(pdf_path)
        summary = generate_summary(raw_text)
        topic = classify_topic(summary, topic_list)
        audio_path = generate_audio(summary, os.path.basename(pdf_path).replace(".pdf", ""))
        all_summaries.append(summary)
        citations.append({"source": pdf_path, "topic": topic, "audio": audio_path})

    # --- Process DOIs ---
    for doi in doi_list:
        print(f"🌐 Processing DOI: {doi}")
        metadata = resolve_doi(doi)
        if "error" not in metadata:
            abstract = metadata.get("abstract", "")
            abstract = abstract.replace("<jats:p>", "").replace("</jats:p>", "") if abstract else ""
            meta_text = f"Title: {metadata['title']}\nJournal: {metadata['journal']}\nAuthors: {', '.join(metadata['authors'])}\n\nAbstract: {abstract}"
            summary = generate_summary(meta_text)
            topic = classify_topic(summary, topic_list)
            audio_path = generate_audio(summary, doi.replace("/", "_"))
            all_summaries.append(summary)
            citations.append({"source": doi, "topic": topic, "audio": audio_path})
        else:
            print("❌ DOI not found or invalid.")

    # --- Process URLs ---
    for url in urls:
        print(f"🌐 Processing URL: {url}")
        content = fetch_url_text(url)
        summary = generate_summary(content)
        topic = classify_topic(summary, topic_list)
        filename = url.replace("https://", "").replace("http://", "").replace("/", "_")
        audio_path = generate_audio(summary, filename[:30])  # trim filename
        all_summaries.append(summary)
        citations.append({"source": url, "topic": topic, "audio": audio_path})

    # --- Final Cross-Paper Summary ---
    if all_summaries:
        print("🧠 Synthesizing final audio summary from all papers...")
        final_summary = synthesize_across_papers(all_summaries)
        synthesis_audio_path = generate_audio(final_summary, "final_synthesis")
    else:
        final_summary = ""
        synthesis_audio_path = None

    return {
        "synthesis": final_summary,
        "synthesis_audio": synthesis_audio_path,
        "citations": citations
    }

# ========================== #
#   FASTAPI ENDPOINTS
# ========================== #

@app.get("/")
async def root():
    return {"message": "Research Paper Podcast System API"}

@app.post("/process")
async def process_papers(
    pdf_files: List[UploadFile] = File([]),
    data: str = Form("{}")
):
    try:
        # Parse the JSON data
        json_data = json.loads(data)
        topic_list = json_data.get("topic_list", [])
        doi_list = json_data.get("doi_list", [])
        urls = json_data.get("urls", [])
        
        # Save uploaded PDF files temporarily
        pdf_paths = []
        for pdf_file in pdf_files:
            if pdf_file.filename.endswith('.pdf'):
                temp_path = os.path.join(OUTPUT_DIR, pdf_file.filename)
                with open(temp_path, "wb") as buffer:
                    content = await pdf_file.read()
                    buffer.write(content)
                pdf_paths.append(temp_path)
        
        # Run the system
        result = run_system(
            pdf_files=pdf_paths,
            topic_list=topic_list,
            doi_list=doi_list,
            urls=urls
        )
        
        return result
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    audio_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(audio_path):
        return FileResponse(audio_path, media_type="audio/mpeg")
    else:
        return {"error": "Audio file not found"}

# ========================== #
#   MAIN MENU (CLI)
# ========================== #
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        # Run as API server
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # Run as CLI
        print("=== 🎧 RESEARCH PAPER PODCAST SYSTEM ===")
        print("Select input method(s):")
        print("1. Upload multiple PDFs")
        print("2. Enter multiple DOIs")
        print("3. Enter paper URLs")
        print("4. Exit")

        choice = input("\nEnter your choice(s) separated by commas (e.g., 1,2): ")

        topic_input = input("📌 (Optional) Enter topics for classification, separated by commas (or leave blank): ").strip()
        topics = [t.strip() for t in topic_input.split(",")] if topic_input else []

        pdf_paths = []
        doi_list = []
        url_list = []

        if "1" in choice:
            paths_input = input("Enter PDF file paths separated by commas: ").strip()
            pdf_paths = [p.strip() for p in paths_input.split(",")]

        if "2" in choice:
            dois_input = input("Enter DOIs separated by commas: ").strip()
            doi_list = [d.strip() for d in dois_input.split(",")]

        if "3" in choice:
            urls_input = input("Enter paper URLs separated by commas: ").strip()
            url_list = [u.strip() for u in urls_input.split(",")]

        if "4" in choice:
            print("👋 Exiting...")
            exit()

        result = run_system(
            pdf_files=pdf_paths,
            topic_list=topics,
            doi_list=doi_list,
            urls=url_list
        )

        print("\n✅ PROCESS COMPLETE\n")
        print("🔊 === SUMMARY ===\n")
        print(result["synthesis"] or "No synthesis available.")

        if result["synthesis_audio"]:
            print(f"\n🎧 Audio file saved at: {result['synthesis_audio']}")

        print("\n📚 === CITATIONS ===\n")
        for citation in result["citations"]:
            print(f"- Source: {citation['source']}")
            print(f"  Topic: {citation['topic']}")
            print(f"  Audio: {citation['audio']}\n")
