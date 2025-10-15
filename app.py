import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4o-mini")
SYSTEM_PROMPT = """You are LearningBuddy, a bilingual educational chatbot for students in Grades 1–12. 
Follow these rules:
1. Be friendly, patient, and encouraging
2. Adapt explanations to the student's grade level
3. Use simple language and short sentences
4. Include examples and visual descriptions
5. Be positive and supportive"""

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
    </style>
""", unsafe_allow_html=True)

# Initialize session state with default values
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", 
         "content": "👋 Hello! I'm LearningBuddy. Which language would you like to learn in? / नमस्ते! आप किस भाषा में सीखना चाहेंगे?"
        }
    ]
    st.session_state.language = "English"
    st.session_state.subject = "Science"
    st.session_state.grade = 6

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

# Chat input
if prompt := st.chat_input("Type your question here... / अपना प्रश्न यहाँ टाइप करें..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Show typing indicator
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
    
    # Prepare the API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Add context to the prompt
    context = f"""Language: {st.session_state.language}
Subject: {st.session_state.subject}
Class: {st.session_state.grade}

Student's question: {prompt}

Please provide a helpful, age-appropriate response in {st.session_state.language}."""
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": context}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        # Make the API call
       # In your app.py, update the API call to:
response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",  # Updated URL
    headers=headers,
    json=payload,
    timeout=30  # Add timeout
        response.raise_for_status()
        
        # Get the response
        data = response.json()
        assistant_response = data["choices"][0]["message"]["content"]
        
        # Update the chat
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        
        # Update the message
        message_placeholder.markdown(assistant_response)
        
    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        message_placeholder.markdown(error_msg)
