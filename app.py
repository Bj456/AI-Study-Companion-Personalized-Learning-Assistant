import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

# Configuration - Use Streamlit secrets for production, .env for local
try:
    # Try to get API key from Streamlit secrets (for Streamlit Cloud)
    API_KEY = st.secrets["OPENROUTER_API_KEY"]
    MODEL = st.secrets.get("MODEL", "gpt-4o-mini")
except:
    # Fallback to .env file for local development
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    MODEL = os.getenv("MODEL", "gpt-4o-mini")

# Validate API key
if not API_KEY or API_KEY == "your_openrouter_api_key_here":
    st.error("🚨 API Key Missing!")
    st.warning("""
    For **Streamlit Cloud deployment**, add your API key to Streamlit secrets:
    1. Go to your Streamlit Cloud app dashboard
    2. Navigate to "Secrets" in the app settings
    3. Add: `OPENROUTER_API_KEY = "your_actual_api_key_here"`

    For **local development**, update the .env file with your API key.

    **Note:** Never commit API keys to your repository!
    """)
    st.stop()  # Stop execution until API key is configured

# System Prompt
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

def get_offline_response(question, subject, grade, language):
    """Provide basic offline responses when API is not accessible."""
    responses = {
        "photosynthesis": {
            "English": "Photosynthesis is how plants make their food using sunlight! 🌱☀️ Plants take in carbon dioxide from the air and water from the soil, and use sunlight to turn them into glucose (sugar) and oxygen. The green pigment chlorophyll helps capture sunlight. This process happens in the leaves of plants.",
            "हिंदी": "प्रकाश संश्लेषण पौधों का भोजन बनाने का तरीका है जो सूरज की रोशनी का उपयोग करता है! 🌱☀️ पौधे हवा से कार्बन डाइऑक्साइड और मिट्टी से पानी लेते हैं, और सूरज की रोशनी का उपयोग करके उन्हें ग्लूकोज (चीनी) और ऑक्सीजन में बदल देते हैं। हरी वर्णक क्लोरोफिल सूरज की रोशनी को पकड़ने में मदद करता है। यह प्रक्रिया पौधों की पत्तियों में होती है।"
        },
        "science": {
            "English": "Science helps us understand how the world works! 🔬 It includes biology (study of living things), chemistry (study of matter), and physics (study of energy and forces). Scientists use experiments and observations to learn new things.",
            "हिंदी": "विज्ञान हमें दुनिया कैसे काम करती है यह समझने में मदद करता है! 🔬 इसमें जीव विज्ञान (जीवित चीजों का अध्ययन), रसायन विज्ञान (पदार्थ का अध्ययन), और भौतिकी (ऊर्जा और बलों का अध्ययन) शामिल हैं। वैज्ञानिक नए चीजें सीखने के लिए प्रयोग और अवलोकन का उपयोग करते हैं।"
        }
    }
    
    # Simple keyword matching for basic responses
    question_lower = question.lower()
    
    if "photosynthesis" in question_lower or "प्रकाश संश्लेषण" in question_lower:
        topic = "photosynthesis"
    elif any(word in question_lower for word in ["science", "विज्ञान", "what is science", "विज्ञान क्या है"]):
        topic = "science"
    else:
        topic = None
    
    if topic and topic in responses:
        return responses[topic].get(language, responses[topic]["English"])
    else:
        return f"I'm currently in offline mode and can't provide detailed answers. Please try again when you have internet connection. For now, I can suggest watching educational videos on YouTube about your topic: '{question}'"

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
                "https://openrouter.ai/api/v1/chat/completions",  # Fixed URL without 'api.'
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
            
        except requests.exceptions.ConnectionError as e:
            if "NameResolutionError" in str(e) or "Name or service not known" in str(e):
                # Try offline mode as fallback
                assistant_response = get_offline_response(prompt, st.session_state.subject, st.session_state.grade, st.session_state.language)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                message_placeholder.markdown(assistant_response)
                st.warning("🔄 Using offline mode - some features may be limited")
            else:
                error_msg = f"🔌 Connection Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                message_placeholder.markdown(error_msg)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"🚫 Network Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            message_placeholder.markdown(error_msg)
            
        except Exception as e:
            error_msg = f"❌ Unexpected Error: {str(e)}"
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
