from langchain_groq import ChatGroq
import streamlit as st
import os

os.environ["GROQ_API_KEY"] = "YOUR_API_KEY"


llm = ChatGroq(model="llama3-8b-8192",temperature=0.6)

def query_and_answer(query_text, k=2): 
    if not st.session_state.vector_db:
        return "Please upload and process presentations first."
        
    results = st.session_state.vector_db.similarity_search(query_text, k=k)
    context = "\n\n".join([doc.page_content for doc in results])

    prompt = f"""Please provide a clear and concise answer to the following question based on the given context.
    If the context doesn't contain enough information to answer the question, please say so.

    Context:
    {context}

    Question: {query_text}

    Answer:"""
    
    answer = llm.invoke(prompt)
    return answer.content

if __name__ == "__main__":
    user_query = "explain uninformed search"
    print("Answer:\n", query_and_answer(user_query))
