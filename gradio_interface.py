"""
Gradio Interface for Research Paper Podcast System
Alternative frontend using Gradio for easy deployment and sharing
"""

import gradio as gr
import os
import tempfile
from typing import List, Optional

# Import the backend processing function
from main import run_system

def process_papers_and_create_podcast(
    pdf_files,
    doi_string,
    url_string,
    topic_string
):
    """
    Process research papers and generate audio summaries using Gradio interface
    
    Args:
        pdf_files: List of uploaded PDF files
        doi_string: Comma-separated DOIs
        url_string: Comma-separated URLs
        topic_string: Comma-separated topics
    
    Returns:
        Tuple of (synthesis_text, synthesis_audio, citations_output)
    """
    
    try:
        # Format inputs for the backend function
        pdf_paths = [f.name for f in pdf_files] if pdf_files else []
        doi_list = [d.strip() for d in doi_string.split(",") if d.strip()] if doi_string else []
        url_list = [u.strip() for u in url_string.split(",") if u.strip()] if url_string else []
        topic_list = [t.strip() for t in topic_string.split(",") if t.strip()] if topic_string else []
        
        print("🎧 Processing Research Papers...")
        print(f"  📄 PDFs: {len(pdf_paths)} files")
        print(f"  🌐 DOIs: {len(doi_list)} entries")
        print(f"  🔗 URLs: {len(url_list)} entries")
        print(f"  🎯 Topics: {len(topic_list)} entries")

        # Validate inputs
        if not pdf_paths and not doi_list and not url_list:
            return (
                "❌ Error: Please provide at least one input (PDFs, DOIs, or URLs)",
                None,
                "No processing performed due to missing inputs."
            )

        # Call the backend system
        result = run_system(
            pdf_files=pdf_paths,
            doi_list=doi_list,
            urls=url_list,
            topic_list=topic_list
        )

        # Prepare outputs for the Gradio components
        synthesis_text = result.get("synthesis", "No synthesis available.")
        synthesis_audio = result.get("synthesis_audio")
        
        # Format citations output
        citations_output = "### 📚 Individual Paper Summaries & Audio\n\n"
        if result.get("citations"):
            for i, citation in enumerate(result["citations"], 1):
                citations_output += (
                    f"#### Paper {i}\n"
                    f"**Source:** {citation['source']}\n"
                    f"**Topic:** {citation['topic']}\n"
                    f"**Audio File:** {citation['audio']}\n\n"
                )
        else:
            citations_output += "No individual papers were processed."

        print("✅ Processing completed successfully!")
        return synthesis_text, synthesis_audio, citations_output
        
    except Exception as e:
        error_msg = f"❌ Error during processing: {str(e)}"
        print(error_msg)
        return error_msg, None, "Processing failed. Please check your inputs and try again."

def clear_inputs():
    """Clear all input fields"""
    return None, "", "", ""

def show_example():
    """Show example inputs"""
    example_dois = "10.1016/j.cell.2023.01.001, 10.1038/s41586-023-05988-x"
    example_urls = "https://arxiv.org/abs/2301.12345, https://www.nature.com/articles/s41586-023-05988-x"
    example_topics = "machine learning, quantum computing, biology"
    return None, example_dois, example_urls, example_topics

# Define the Gradio interface
with gr.Blocks(
    theme=gr.themes.Soft(),
    title="🎧 Research Paper Podcast System",
    css="""
    .gradio-container {
        max-width: 1200px !important;
        margin: 0 auto !important;
    }
    .header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    """
) as demo:
    
    # Header
    gr.HTML("""
    <div class="header">
        <h1>🎧 Research Paper Podcast System</h1>
        <p>Transform research papers into engaging audio podcasts using AI</p>
    </div>
    """)
    
    gr.Markdown(
        """
        ### 🚀 How it Works
        
        This AI-powered system helps you quickly understand and synthesize research papers by generating
        an audio podcast. You can provide one or more inputs in the form of PDFs, DOIs, or URLs.
        
        **Features:**
        - 📄 **PDF Processing**: Upload research papers directly
        - 🌐 **DOI Fetching**: Automatic metadata retrieval from CrossRef
        - 🔗 **URL Scraping**: Extract content from research paper URLs
        - 🧠 **AI Summarization**: State-of-the-art DistilBART model
        - 🎧 **Audio Generation**: High-quality text-to-speech conversion
        - 🔄 **Cross-Paper Synthesis**: Combine insights from multiple papers
        
        ---
        """
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### 📥 Input Research Papers")
            
            pdf_input = gr.Files(
                label="📄 Upload PDF Files", 
                file_types=[".pdf"], 
                file_count="multiple",
                info="Upload one or more PDF research papers"
            )
            
            doi_input = gr.Textbox(
                label="🌐 Enter DOIs",
                placeholder="e.g., 10.1016/j.cell.2023.01.001, 10.1038/s41586-023-05988-x",
                info="Enter DOIs separated by commas (no spaces needed)"
            )
            
            url_input = gr.Textbox(
                label="🔗 Enter Paper URLs",
                placeholder="e.g., https://arxiv.org/abs/2301.12345, https://www.nature.com/articles/s41586-023-05988-x",
                info="Enter URLs separated by commas (no spaces needed)"
            )
            
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Configuration")
            
            topic_input = gr.Textbox(
                label="🎯 Optional: Topics for Classification",
                placeholder="e.g., machine learning, quantum computing, biology",
                info="This helps in classifying the content of each paper"
            )
            
            with gr.Row():
                submit_btn = gr.Button("🚀 Generate Podcast", variant="primary", size="lg")
                clear_btn = gr.Button("🗑️ Clear", variant="secondary")
                example_btn = gr.Button("📋 Example", variant="secondary")
    
    gr.Markdown("---")
    
    with gr.Row():
        gr.Markdown("### 🎙️ Podcast Output")
    
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("#### 📝 Final Synthesis Summary")
            final_summary_output = gr.Textbox(
                label="Combined Summary", 
                lines=12, 
                interactive=False,
                show_label=False
            )
        with gr.Column(scale=1):
            gr.Markdown("#### 🎧 Final Audio Podcast")
            synthesis_audio_output = gr.Audio(
                label="Podcast Audio", 
                type="filepath", 
                autoplay=False,
                interactive=False,
                show_label=False
            )
    
    gr.Markdown("---")
    
    citations_output = gr.Markdown("### 📚 Individual Paper Details")

    # Status indicator
    status_output = gr.Textbox(
        label="Status",
        value="Ready to process papers. Upload files or enter DOIs/URLs above.",
        interactive=False
    )

    # Connect button clicks to functions
    submit_btn.click(
        fn=process_papers_and_create_podcast,
        inputs=[pdf_input, doi_input, url_input, topic_input],
        outputs=[final_summary_output, synthesis_audio_output, citations_output]
    ).then(
        fn=lambda: "✅ Processing completed! Check the results above.",
        outputs=[status_output]
    )
    
    clear_btn.click(
        fn=clear_inputs,
        outputs=[pdf_input, doi_input, url_input, topic_input]
    ).then(
        fn=lambda: "🗑️ Inputs cleared. Ready for new processing.",
        outputs=[status_output]
    )
    
    example_btn.click(
        fn=show_example,
        outputs=[pdf_input, doi_input, url_input, topic_input]
    ).then(
        fn=lambda: "📋 Example inputs loaded. Click 'Generate Podcast' to process.",
        outputs=[status_output]
    )

    # Footer
    gr.Markdown(
        """
        ---
        
        ### 🔧 Technical Details
        
        **Backend Technologies:**
        - FastAPI for API endpoints
        - PyPDF2 for PDF text extraction
        - BeautifulSoup for web scraping
        - Transformers (DistilBART) for summarization
        - Google Text-to-Speech for audio generation
        
        **Processing Pipeline:**
        1. **Input Processing**: Extract text from PDFs, fetch DOI metadata, scrape URLs
        2. **Content Analysis**: Classify topics and generate summaries
        3. **Cross-Paper Synthesis**: Combine insights from multiple papers
        4. **Audio Generation**: Convert summaries to high-quality audio
        5. **Output Delivery**: Provide both text and audio results
        
        ---
        
        <div style="text-align: center; color: #666; font-size: 0.9em;">
        🎧 Research Paper Podcast System | Powered by AI & FastAPI
        </div>
        """
    )

if __name__ == "__main__":
    print("🎧 Starting Research Paper Podcast System (Gradio Interface)...")
    print("🌐 Interface will be available at: http://localhost:7860")
    print("📚 API Server should be running at: http://localhost:8000")
    print("🎯 Make sure the backend processing functions are available")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    ) 