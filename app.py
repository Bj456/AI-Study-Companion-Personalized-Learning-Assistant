import streamlit as st
from helper import get_personalized_answer
import threading

st.set_page_config(page_title="AI Study Companion", page_icon="🎓", layout="centered", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    /* Mobile-friendly styles */
    @media (max-width: 768px) {
        .stTextInput, .stSelectbox, .stTextArea, .stButton {
            font-size: 16px !important;
            padding: 12px !important;
        }
        .stSidebar {
            padding: 10px !important;
        }
        h1 {
            font-size: 24px !important;
        }
        h4 {
            font-size: 18px !important;
        }
        .stMarkdown {
            font-size: 14px !important;
        }
    }
    /* General improvements for touch */
    .stButton button {
        height: 50px !important;
        font-size: 16px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Sidebar: Student Profile ----------
st.sidebar.header("🧠 Student Profile")

if "name" not in st.session_state:
    st.session_state.name = ""
st.session_state.name = st.sidebar.text_input("Enter your name:", value=st.session_state.name)

if "mbti" not in st.session_state:
    st.session_state.mbti = "INTJ"
st.session_state.mbti = st.sidebar.selectbox(
    "Select your MBTI Type:", ["INTJ", "ENFP", "ISTP", "ESFJ", "INFP", "ENTP"], index=["INTJ", "ENFP", "ISTP", "ESFJ", "INFP", "ENTP"].index(st.session_state.mbti)
)

if "learning_style" not in st.session_state:
    st.session_state.learning_style = "Visual"
st.session_state.learning_style = st.sidebar.selectbox(
    "Select your Learning Style:", ["Visual", "Auditory", "Kinesthetic"], index=["Visual", "Auditory", "Kinesthetic"].index(st.session_state.learning_style)
)

if "language" not in st.session_state:
    st.session_state.language = "English"
st.session_state.language = st.sidebar.radio("Choose Language:", ["English", "Hindi"])

# ---------- Main Area ----------
st.markdown("### Ask Your Question 👇")
st.info("📱 Tip: For the best experience on mobile, use landscape mode or expand your browser!")
question = st.text_area("Enter your question here...", key="question_input", height=150)

# Initialize answer in session state
if "answer" not in st.session_state:
    st.session_state.answer = ""

# ---------- Function to fetch answer in a separate thread ----------
def fetch_answer():
    st.session_state.answer = get_personalized_answer(
        question, st.session_state.mbti, st.session_state.learning_style,
        language="hi" if st.session_state.language=="Hindi" else "en",
        name=st.session_state.name
    )

# ---------- Button ----------
if st.button("Get Personalized Answer"):
    with st.spinner("Generating your personalized answer..."):
        thread = threading.Thread(target=fetch_answer)
        thread.start()
        thread.join()  # Wait here so spinner shows until done

# ---------- Display Answer ----------
st.markdown("#### 🧾 Answer:")
st.write(st.session_state.answer)
