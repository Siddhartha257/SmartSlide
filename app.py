import streamlit as st
from query import query_and_answer
from model import initialize_db, get_or_create_summary, process_ppt
from quiz import display_quiz
import os
import shutil
import atexit


st.set_page_config(
    page_title="SmartSlide",
    page_icon="📊",
    layout="wide"
)


st.markdown("""
    <style>
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .stTextArea > div > div > textarea {
        font-size: 16px;
    }
    .answer-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    .summary-box {
        background-color: #e6f3ff;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #2b313e;
        color: white;
    }
    .chat-message.assistant {
        background-color: #f0f2f6;
    }
    .chat-message .content {
        display: flex;
        flex-direction: column;
    }
    </style>
    """, unsafe_allow_html=True)

# Cleanup function to remove temporary files
def cleanup():
    """Clean up temporary files when the app exits"""
    try:
        # Remove temporary uploads
        if os.path.exists("temp_uploads"):
            shutil.rmtree("temp_uploads")
            
       
        os.makedirs("temp_uploads", exist_ok=True)
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")


atexit.register(cleanup)


if 'vector_db' not in st.session_state:
    st.session_state.vector_db = None
if 'all_chunks' not in st.session_state:
    st.session_state.all_chunks = []
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'show_summary' not in st.session_state:
    st.session_state.show_summary = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar
with st.sidebar:
    st.title("📊 SmartSlide")
    st.markdown("---")
    
    # File uploader
    st.subheader("Upload Presentations")
    uploaded_files = st.file_uploader(
        "Choose PowerPoint files",
        type=['pptx'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        # Save uploaded files
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        ppt_paths = []
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            ppt_paths.append(file_path)
        
        if st.button("Process Presentations", type="primary"):
            with st.spinner("Processing presentations..."):
                st.session_state.vector_db, st.session_state.all_chunks = initialize_db(ppt_paths)
                
                if 'ppt_summary' in st.session_state:
                    del st.session_state.ppt_summary
                st.session_state.chat_history = []
                st.success("Presentations processed successfully!")
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### Navigation")
    page = st.radio(
        "Select a page:",
        ["Ask Questions", "View Summary", "Take Quiz"]
    )

# Main content
if page == "Ask Questions":
    st.title("❓ Ask Questions")
    
    if not st.session_state.all_chunks:
        st.info("Please upload and process presentations first.")
    else:
        question = st.text_input("Enter your question about the presentation:",placeholder="type your query..")
        if question:
            with st.spinner("Thinking..."):
                answer = query_and_answer(question)
                st.markdown("### Answer:")
                st.write(answer)

elif page == "View Summary":
    st.title("📝 Presentation Summary")
    
    if not st.session_state.all_chunks:
        st.info("Please upload and process presentations first.")
    else:
        with st.spinner("Generating summary..."):
            summary = get_or_create_summary(st.session_state.all_chunks, "Provide a comprehensive summary of the presentation content.")
            st.markdown(summary)

else:  # Quiz page
    display_quiz()

st.sidebar.info("Please note: Analysis of larger files may take longer than usual due to their size.")
st.sidebar.markdown("""
    ### About
    This app analyzes PowerPoint presentations and answers questions about their content using AI.
    
    ### How to use
    1. Upload your PowerPoint files
    2. Click 'Process Presentations'
    3. Ask questions or get a summary
    4. View the AI-generated responses
    """) 