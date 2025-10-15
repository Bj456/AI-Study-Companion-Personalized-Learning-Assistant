import streamlit as st
from helper import get_personalized_answer

st.set_page_config(page_title="AI Study Companion", page_icon="🎓", layout="wide")

st.markdown(
    """
    <h1 style='text-align:center; color:#2B547E;'>🎓 AI Study Companion</h1>
    <h4 style='text-align:center;'>Your Personalized Learning Assistant</h4>
    """,
    unsafe_allow_html=True
)

st.sidebar.header("🧠 Student Profile")
mbti = st.sidebar.selectbox("Select your MBTI Type:", ["INTJ", "ENFP", "ISTP", "ESFJ", "INFP", "ENTP"])
learning_style = st.sidebar.selectbox("Select your Learning Style:", ["Visual", "Auditory", "Kinesthetic"])
language = st.sidebar.radio("Choose Language:", ["English", "Hindi"])

st.markdown("### Ask Your Question 👇")
question = st.text_area("Enter your question here...")

if st.button("Get Personalized Answer"):
    lang_code = "hi" if language == "Hindi" else "en"
    answer = get_personalized_answer(question, mbti, learning_style, language=lang_code)
    st.markdown("#### 🧾 Answer:")
    st.write(answer)
