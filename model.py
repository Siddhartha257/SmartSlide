from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

import uuid
import os
import streamlit as st
import shutil

# Directory to save Chroma DB
CHROMA_PATH = "./chroma_db"

def cleanup_chroma_db():
    """Clean up the Chroma database directory"""
    try:
        if os.path.exists(CHROMA_PATH):
           
            shutil.rmtree(CHROMA_PATH, ignore_errors=True)
            
            if os.path.exists(CHROMA_PATH):
                os.system(f"rm -rf {CHROMA_PATH}")
            print("Chroma database cleaned up successfully")
    except Exception as e:
        print(f"Error cleaning up Chroma database: {str(e)}")


if 'cleanup_registered' not in st.session_state:
    st.session_state.cleanup_registered = True
    st.cache_data.clear()  #

def process_ppt(ppt_path):

    loader = UnstructuredPowerPointLoader(ppt_path)
    data = loader.load()
    return text_splitter(data)

def text_splitter(documents: list[Document]):
    """Split content into smaller chunks"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  
        chunk_overlap=50,  
        is_separator_regex=False
    )
    return splitter.split_documents(documents)

def get_embeddings():
    """Get HuggingFace embeddings"""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def add_to_chroma(chunks):
    """Store documents in Chroma vector DB"""
    
    if os.path.exists(CHROMA_PATH):
        cleanup_chroma_db()
    
    os.makedirs(CHROMA_PATH, exist_ok=True)
    
    os.chmod(CHROMA_PATH, 0o777)
    
    ids = [str(uuid.uuid4()) for _ in chunks]

    try:
       
        db = Chroma.from_documents(
            documents=chunks,
            embedding=get_embeddings(),
            persist_directory=CHROMA_PATH
        )
        
        
        
        return db
        
    except Exception as e:
        print(f"Error creating Chroma database: {str(e)}")
        
        cleanup_chroma_db()
        os.makedirs(CHROMA_PATH, exist_ok=True)
        os.chmod(CHROMA_PATH, 0o777)
        
        db = Chroma.from_documents(
            documents=chunks,
            embedding=get_embeddings(),
            persist_directory=CHROMA_PATH
        )
        db.persist()
        return db

def summarize_chunk(chunk_text, llm):
    """Summarize a single chunk of text"""
    prompt = f"""Please provide a concise summary of the following content, focusing on key points and main ideas:

Content:
{chunk_text}

Summary:"""
    summary = llm.invoke(prompt)
    return summary.content

def get_or_create_summary(chunks, query=None):
    """Get or create a summary of the presentation content"""
    if query is None:
        query = "Provide a comprehensive summary of the presentation content."
    

    return summarize_ppt(chunks)

def summarize_ppt(chunks):
    """Efficiently summarize the entire PPT content with fewer API calls."""
    from langchain_groq import ChatGroq
    
    llm = ChatGroq(model="llama3-8b-8192")
    
    # Combine all chunks into a single text
    all_text = "\n\n".join(chunk.page_content for chunk in chunks)
    
 
    estimated_tokens = len(all_text) // 4
    max_input_tokens = 6000  
    
    # If content fits within token limit, process in single call
    if estimated_tokens <= max_input_tokens:
        return summarize_chunk(all_text, llm)
    
    # For large content, use intelligent chunking
    # Split into fewer, larger chunks (2-4 chunks max) based on content size
    if estimated_tokens <= max_input_tokens * 2:
        num_chunks = 2
    elif estimated_tokens <= max_input_tokens * 3:
        num_chunks = 3
    else:
        num_chunks = 4
    
    chunk_size = len(all_text) // num_chunks
    overlap_size = chunk_size // 10  # 10% overlap to maintain context
    
    parts = []
    for i in range(num_chunks):
        start = max(0, i * chunk_size - overlap_size)
        end = min(len(all_text), (i + 1) * chunk_size + overlap_size)
        
        # Avoid cutting words in half - find nearest space
        if end < len(all_text):
            while end < len(all_text) and all_text[end] != ' ':
                end += 1
        
        parts.append(all_text[start:end])
    
   
    parts = [part.strip() for part in parts if part.strip()]
    
    
    if len(parts) == 1:
        return summarize_chunk(parts[0], llm)
    
    
    partial_summaries = []
    for i, part in enumerate(parts):
        enhanced_prompt = f"""Please provide a detailed summary of the following content section ({i+1} of {len(parts)}), focusing on key points, main ideas, and important details:

Content:
{part}

Summary:"""
        
        summary = llm.invoke(enhanced_prompt)
        partial_summaries.append(summary.content)
    
    
    combined_summary = "\n\n".join(partial_summaries)
    
    final_prompt = f"""Based on the following section summaries from a presentation, create a comprehensive final summary that captures all key points and maintains logical flow:

Section Summaries:
{combined_summary}

Comprehensive Summary:"""
    
    final_summary = llm.invoke(final_prompt)
    return final_summary.content

def initialize_db(ppt_paths):
    """Initialize the vector database with multiple PPTs"""
   
    cleanup_chroma_db()
    
    all_chunks = []
    
    # Process all PPTs first
    for ppt_path in ppt_paths:
        try:
            chunks = process_ppt(ppt_path)
            all_chunks.extend(chunks)
        except Exception as e:
            st.error(f"Error processing {ppt_path}: {str(e)}")
            continue
    
    if not all_chunks:
        st.error("No content could be processed from the uploaded files.")
        return None, []
    

    vector_db = add_to_chroma(all_chunks)
    return vector_db, all_chunks


def query_vector_db(db, query_text, k=3):
    results = db.similarity_search(query_text, k=k)
    for i, doc in enumerate(results):
        print(doc.page_content)
        print()



