import openai
import streamlit as st

# ✅ Load your API key from Streamlit secrets
openai.api_key = st.secrets["OPENROUTER_API_KEY"]
openai.base_url = "https://openrouter.ai/api/v1"

def get_personalized_answer(question, mbti, learning_style, language="en"):
    # Create the adaptive prompt
    if language == "hi":
        prompt = f"""
        आप एक विशेषज्ञ शिक्षक हैं जो छात्रों की MBTI व्यक्तित्व और सीखने की शैली को समझते हैं।
        छात्र की MBTI प्रकार है {mbti} और उसकी सीखने की शैली है {learning_style}।
        इस प्रश्न का उत्तर छात्रों के स्तर पर, आसान भाषा में और विस्तार से दें:
        {question}
        """
    else:
        prompt = f"""
        You are an expert teacher who adapts explanations according to the student's MBTI type and learning style.
        The student's MBTI is {mbti}, and their learning style is {learning_style}.
        Give a detailed, easy-to-understand answer for the question:
        {question}
        """

    # 🧠 Make API call
    response = openai.chat.completions.create(
        model="openai/gpt-4o-mini",  # You can choose other models
        messages=[
            {"role": "system", "content": "You are a helpful AI study assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    # ✅ Fix: safely extract text
    try:
        return response.choices[0].message["content"]
    except Exception as e:
        # If response format changes or fails
        st.error("⚠️ Error extracting response: " + str(e))
        st.write("Full response object:", response)
        return "Sorry, I couldn’t process that. Please try again."
