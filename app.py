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

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", 
         "content": "👋 Hello! I'm LearningBuddy. Which language would you like to learn in? / नमस्ते! आप किस भाषा में सीखना चाहेंगे?"
        }
    ]
    st.session_state.language = None
    st.session_state.subject = None
    st.session_state.grade = None

# Sidebar for settings
with st.sidebar:
    st.title("⚙️ Settings")
    st.session_state.language = st.radio(
        "Choose Language / भाषा चुनें:",
        ["English", "हिंदी (Hindi)"],
        index=0 if st.session_state.get("language") == "English" else 1 if st.session_state.get("language") == "हिंदी (Hindi)" else 0
    )
    
    st.session_state.subject = st.selectbox(
        "Select Subject / विषय चुनें:",
        ["Science", "Maths", "English", "EVS", "Hindi"],
        index=["Science", "Maths", "English", "EVS", "Hindi"].index(st.session_state.get("subject", "Science"))
    )
    
    st.session_state.grade = st.selectbox(
        "Select Class / कक्षा चुनें:",
        list(range(1, 13)),
        index=st.session_state.get("grade", 6) - 1 if st.session_state.get("grade") else 5
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
        response = requests.post(
            "https://api.openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
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
st.session_state.language = st.sidebar.radio("Choose Language:", ["English", "Hindi"])

# Initialize question in session state
if "question" not in st.session_state:
    st.session_state.question = ""

# ---------- Main Area ----------
st.markdown("### Ask Your Question 👇")
st.info("📱 Tip: For the best experience on mobile, use landscape mode or expand your browser!")
st.session_state.question = st.text_area("Enter your question here...", value=st.session_state.question, key="question_input", height=150)

# Initialize answer in session state
if "answer" not in st.session_state:
    st.session_state.answer = ""

# ---------- Function to fetch answer in a separate thread ----------
def fetch_answer():
    st.session_state.answer = get_personalized_answer(
        st.session_state.question, st.session_state.mbti, st.session_state.learning_style,
        language="hi" if st.session_state.language=="Hindi" else "en",
        name=st.session_state.name
    )

# ---------- Button ----------
if st.button("Get Personalized Answer"):
    if not st.session_state.question.strip():
        st.error("Please enter a question first.")
    else:
        with st.spinner("Generating your personalized answer..."):
            thread = threading.Thread(target=fetch_answer)
            thread.start()
            # Removed time.sleep to prevent UI freeze
        st.success("Answer is being generated! Check below in a moment.")

# ---------- Display Answer ----------
if st.session_state.answer:
    st.markdown("#### 🧾 Answer:")
    st.write(st.session_state.answer)
else:
    st.markdown("#### 🧾 Answer:")
    st.write("Your personalized answer will appear here after clicking the button.")
