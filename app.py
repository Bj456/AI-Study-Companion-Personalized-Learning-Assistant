import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4o-mini")
SYSTEM_PROMPT = """You are LearningBuddy, a friendly, bilingual AI tutor for children in Grades 1–12. 

Your role is to:
1. Provide clear, age-appropriate explanations in simple language
2. Use emojis and visual descriptions to make learning engaging
3. Be patient, encouraging, and supportive
4. Adapt content to the student's grade level and language
5. Maintain a positive and motivating tone

For quizzes:
- Generate 10 relevant questions with 4 options each
- Include a mix of difficulty levels
- Provide clear feedback for each answer
- Be encouraging regardless of the score

Format your responses with clear sections and use markdown for better readability."""

# Set up the page
st.set_page_config(
    page_title="LearningBuddy AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS for better mobile experience
st.markdown("""
    <style>
    @media (max-width: 768px) {
        .stTextInput, .stTextArea, .stButton, .stSelectbox {
            font-size: 16px !important;
        }
        .stMarkdown {
            font-size: 16px !important;
        }
        .stButton > button {
            width: 100% !important;
            margin: 5px 0 !important;
        }
    }
    .stButton > button {
        background-color: #4CAF50 !important;
        color: white !important;
        border-radius: 10px;
        padding: 10px 20px;
    }
    .stTextArea textarea {
        min-height: 100px;
    }
    .quiz-question {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", 
         "content": "👋 Hello! I'm LearningBuddy. Which language would you like to learn in? / नमस्ते! आप किस भाषा में सीखना चाहेंगे?"
        }
    ]
    st.session_state.language = "English"
    st.session_state.subject = "Science"
    st.session_state.grade = 6
    st.session_state.waiting_for_video_confirmation = False
    st.session_state.waiting_for_quiz_confirmation = False
    st.session_state.quiz_questions = []
    st.session_state.current_question = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_started = False

# Sidebar for settings
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Language selection
    language_options = ["English", "हिंदी (Hindi)"]
    st.session_state.language = st.radio(
        "Choose Language / भाषा चुनें:",
        language_options,
        index=language_options.index(st.session_state.language) if st.session_state.language in language_options else 0
    )
    
    # Subject selection
    subject_list = ["Science", "Maths", "English", "EVS", "Hindi"]
    st.session_state.subject = st.selectbox(
        "Select Subject / विषय चुनें:",
        subject_list,
        index=subject_list.index(st.session_state.subject) if st.session_state.subject in subject_list else 0
    )
    
    # Grade selection
    try:
        grade_index = int(st.session_state.grade) - 1
        if grade_index < 0 or grade_index > 11:  # Grades 1-12
            grade_index = 5  # Default to grade 6 if out of range
    except:
        grade_index = 5  # Default to grade 6 if there's any error

    st.session_state.grade = st.selectbox(
        "Select Class / कक्षा चुनें:",
        list(range(1, 13)),
        index=grade_index
    )

# Main chat interface
st.title("🎓 LearningBuddy")
st.caption("Your friendly AI study companion for Grades 1-12 / कक्षा 1-12 के लिए आपका दोस्ताना AI साथी")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] in ["user", "assistant"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def parse_quiz_response(response_text):
    """Parse the quiz questions and answers from the AI response."""
    questions = []
    current_question = None
    
    lines = response_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith(('Q', 'Question')) and ('.' in line or ':' in line):
            if current_question:
                questions.append(current_question)
            question_text = line.split(':', 1)[-1].split('.', 1)[-1].strip()
            current_question = {
                'question': question_text,
                'options': [],
                'answer': None
            }
        elif current_question and line and line[0].lower() in 'abcd' and (')' in line or '.' in line or ':' in line):
            option_text = line.split(')', 1)[-1].split(':', 1)[-1].split('.', 1)[-1].strip()
            current_question['options'].append(option_text)
            if 'correct' in line.lower() or 'answer' in line.lower():
                current_question['answer'] = line[0].lower()
        i += 1
    
    if current_question and current_question['options']:
        questions.append(current_question)
    
    return questions[:10]  # Return max 10 questions

# Handle chat input and responses
if prompt := st.chat_input("Type your question here... / अपना प्रश्न यहाँ टाइप करें..."):
    # Reset quiz state for new questions
    if not st.session_state.waiting_for_video_confirmation and not st.session_state.waiting_for_quiz_confirmation:
        st.session_state.quiz_questions = []
        st.session_state.current_question = 0
        st.session_state.quiz_score = 0
        st.session_state.quiz_started = False
    
    # Handle quiz answers
    if st.session_state.waiting_for_quiz_confirmation and prompt.lower() in ['yes', 'y', 'haan', 'हाँ', 'हां']:
        st.session_state.quiz_started = True
        st.session_state.waiting_for_quiz_confirmation = False
        prompt = ""  # Clear the prompt to avoid processing as a new question
    
    # Process regular questions
    if prompt and prompt.strip():
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Show typing indicator
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
        
        try:
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Build context based on the current state
            context = f"""Language: {st.session_state.language}
Subject: {st.session_state.subject}
Grade: {st.session_state.grade}

Student's question: {prompt}

Please provide:
1. A clear, age-appropriate explanation in {st.session_state.language}
2. A relevant YouTube video link (if applicable)
3. A 10-question multiple choice quiz in this format:
   Q1. [Question]?
   a) Option 1
   b) Option 2
   c) Option 3
   d) Option 4
   Answer: [correct_letter]
   
   Continue for 10 questions.

Format your response with clear sections for each part."""
            
            payload = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": context}
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            # Make the API call
            response = requests.post(
                "https://api.openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            # Process the response
            data = response.json()
            assistant_response = data["choices"][0]["message"]["content"]
            
            # Parse quiz questions if present
            quiz_questions = parse_quiz_response(assistant_response)
            if quiz_questions:
                st.session_state.quiz_questions = quiz_questions
                st.session_state.waiting_for_quiz_confirmation = True
            
            # Update the chat
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            message_placeholder.markdown(assistant_response)
            
            # If we have video suggestions, ask if they want to watch
            if any(word in assistant_response.lower() for word in ['youtube', 'video', 'watch']):
                st.session_state.waiting_for_video_confirmation = True
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            message_placeholder.markdown(error_msg)

# Handle quiz flow
if st.session_state.waiting_for_quiz_confirmation and st.session_state.quiz_questions:
    with st.chat_message("assistant"):
        st.markdown("Would you like to take a short quiz to test your understanding? (yes/no)")

# Display current quiz question if quiz is in progress
if st.session_state.quiz_started and st.session_state.quiz_questions:
    if st.session_state.current_question < len(st.session_state.quiz_questions):
        question = st.session_state.quiz_questions[st.session_state.current_question]
        with st.chat_message("assistant"):
            st.markdown(f"**Question {st.session_state.current_question + 1}:** {question['question']}")
            
            # Display options as buttons
            options = question.get('options', [])
            selected = None
            
            for i, option in enumerate(options):
                if st.button(f"{chr(97+i)}) {option}"):
                    selected = chr(97+i)
                    # Check answer
                    if selected == question.get('answer', '').lower():
                        st.session_state.quiz_score += 1
                        st.success("✅ Correct!")
                    else:
                        st.error(f"❌ Incorrect. The correct answer is {question.get('answer', 'unknown')}.")
                    
                    # Move to next question or show results
                    st.session_state.current_question += 1
                    if st.session_state.current_question < len(st.session_state.quiz_questions):
                        st.rerun()
                    else:
                        # Calculate score
                        score = (st.session_state.quiz_score / len(st.session_state.quiz_questions)) * 100
                        
                        # Provide feedback based on score
                        if score < 50:
                            feedback = "You might want to review the material and try again. Would you like to see the explanation again?"
                        elif score < 90:
                            feedback = f"Good job! You scored {score:.0f}%. Would you like to try a similar quiz to improve further?"
                        else:
                            feedback = f"Excellent work! You scored {score:.0f}%. Would you like to try a more challenging quiz?"
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"Quiz complete! Your score: {score:.0f}%. {feedback}"
                        })
                        st.session_state.quiz_started = False
                        st.rerun()
    
    # Add a way to exit the quiz
    if st.button("Exit Quiz"):
        st.session_state.quiz_started = False
        st.session_state.waiting_for_quiz_confirmation = False
        st.rerun()
