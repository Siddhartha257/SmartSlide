# PPT Analyzer

A powerful tool for analyzing and querying PowerPoint presentations using LangChain and Streamlit. This application allows users to upload multiple PowerPoint files, process them, and perform semantic searches on their content.

## Features

- 📂 Upload and analyze multiple PowerPoint files
- 🧠 Generate concise summaries of slide content
- 🔍 Perform semantic search over all slides
- 📝 Generate quiz questions from presentations
- ✅ Check answers and evaluate score
- 📦 Efficient chunking and summarization with minimal API calls
- 🌐 Easy-to-use Streamlit interface
- 🧠 Uses LangChain + Groq + Chroma for backend processing

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided local URL (typically http://localhost:8501)

3. Upload your PowerPoint files using the sidebar interface

4. Use the search functionality to query the content of your presentations

5. View summaries and search results in the main interface

## Project Structure

- `app.py`: Main Streamlit application interface
- `model.py`: Core functionality for PPT processing and querying
- `query.py`: Query handling and response generation
- `utils.py`: Utility functions for file handling and text processing

## Dependencies

The project uses several key libraries:
- Streamlit for the web interface
- LangChain for document processing
- Chroma for vector storage
- Unstructured for PPT parsing
- HuggingFace for embeddings

## Notes

- The application creates a temporary Chroma database for storing document vectors
- Large presentations may take longer to process
- The system automatically handles cleanup of temporary files

