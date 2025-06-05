from langchain_groq import ChatGroq
import streamlit as st
from model import get_or_create_summary
import json

def generate_quiz(chunks):
    """Generate a quiz with 5 questions based on the PPT content"""
    llm = ChatGroq(model="llama3-8b-8192")
    
    # Combine chunks into a single context, but limit the total size
    # Rough estimate: 1 token ≈ 4 characters
    max_chars = 20000  # Conservative limit to stay under 6000 tokens
    context = ""
    for chunk in chunks:
        if len(context) + len(chunk.page_content) > max_chars:
            break
        context += "\n\n" + chunk.page_content
    
    prompt = f"""Create a quiz with 5 multiple-choice questions based on this content.
    Each question should have 4 options (A, B, C, D) and one correct answer.
    Focus on key concepts and important details.
    Format as JSON:
    {{
        "questions": [
            {{
                "question": "question text",
                "options": {{
                    "A": "option A",
                    "B": "option B",
                    "C": "option C",
                    "D": "option D"
                }},
                "correct_answer": "A/B/C/D"
            }}
        ]
    }}

    Content:
    {context}
    """
    
    try:
        response = llm.invoke(prompt)
        # Extract JSON from the response
        json_str = response.content
        # Find the JSON object in the response
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}') + 1
        json_str = json_str[start_idx:end_idx]
        
        quiz_data = json.loads(json_str)
        return quiz_data["questions"]
    except Exception as e:
        st.error(f"Error generating quiz: {str(e)}")
        return None

def evaluate_answers(questions, user_answers):
    """Evaluate user answers and return score and feedback"""
    score = 0
    feedback = []
    
    for i, (question, user_answer) in enumerate(zip(questions, user_answers)):
        is_correct = user_answer == question["correct_answer"]
        if is_correct:
            score += 1
        
        feedback.append({
            "question": question["question"],
            "user_answer": user_answer,
            "correct_answer": question["correct_answer"],
            "is_correct": is_correct
        })
    
    return score, feedback

def display_quiz():
    """Display the quiz interface"""
    st.title("📝 Quiz on Presentation Content")
    
    # Initialize session state for quiz
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = None
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    
    # Generate quiz if not already generated
    if st.session_state.quiz_questions is None and st.session_state.all_chunks:
        with st.spinner("Generating quiz..."):
            questions = generate_quiz(st.session_state.all_chunks)
            if questions is not None:
                st.session_state.quiz_questions = questions
                st.session_state.user_answers = [None] * len(questions)
            else:
                st.error("Failed to generate quiz. Please try again.")
                return
    
    # Display quiz if available
    if st.session_state.quiz_questions:
        st.markdown("### Test Your Understanding")
        st.markdown("Answer the following questions based on the presentation content.")
        
        # Display questions
        for i, question in enumerate(st.session_state.quiz_questions):
            st.markdown(f"**Question {i+1}:** {question['question']}")
            
            if st.session_state.quiz_submitted:
                # Show answers after submission
                for option, text in question["options"].items():
                    if option == question["correct_answer"]:
                        st.markdown(f"✅ {option}. {text}")
                    elif option == st.session_state.user_answers[i]:
                        st.markdown(f"❌ {option}. {text}")
                    else:
                        st.markdown(f"{option}. {text}")
            else:
                # Radio buttons for answers before submission
                selected_option = st.radio(
                    f"Select your answer for Question {i+1}:",
                    options=list(question["options"].keys()),
                    format_func=lambda x: f"{x}. {question['options'][x]}",
                    key=f"quiz_q{i}",
                    label_visibility="collapsed"
                )
                if selected_option:
                    st.session_state.user_answers[i] = selected_option
        
        # Submit button
        if not st.session_state.quiz_submitted:
            if st.button("Submit Quiz", type="primary"):
                if None in st.session_state.user_answers:
                    st.warning("Please answer all questions before submitting.")
                else:
                    st.session_state.quiz_submitted = True
                    score, feedback = evaluate_answers(
                        st.session_state.quiz_questions,
                        st.session_state.user_answers
                    )
                    
                    # Display feedback first
                    st.markdown("### Detailed Feedback:")
                    for i, item in enumerate(feedback):
                        st.markdown(f"**Question {i+1}:**")
                        st.markdown(f"Your answer: {item['user_answer']}")
                        st.markdown(f"Correct answer: {item['correct_answer']}")
                        st.markdown("---")
                    
                    # Display score at the end with enhanced styling
                    st.markdown("---")
                    st.markdown("### 🎯 Final Score")
                    st.markdown(f"""
                    <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                        <h2 style='margin: 0;'>{score}/{len(st.session_state.quiz_questions)}</h2>
                        <p style='margin: 5px 0 0 0;'>Correct Answers</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Reset button
        if st.session_state.quiz_submitted:
            if st.button("Take Quiz Again"):
                st.session_state.quiz_questions = None
                st.session_state.user_answers = []
                st.session_state.quiz_submitted = False
                st.rerun()
    else:
        st.info("Please upload and process presentations first to generate the quiz.") 