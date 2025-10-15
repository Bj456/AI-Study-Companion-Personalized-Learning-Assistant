from openrouter import OpenRouter
import streamlit as st

# Load API key from Streamlit secrets
api_key = st.secrets["OPENROUTER_API_KEY"]

client = OpenRouter(api_key=api_key)

def get_personalized_answer(question, mbti, learning_style, language="en"):
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

    try:
        # Use OpenRouter client chat method
        response = client.chat.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI study assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7
        )
        # Extract the text safely
        return response['choices'][0]['message']['content']

    except Exception as e:
        st.error("⚠️ Error generating answer:")
        st.write(str(e))
        return "Sorry, something went wrong. Please check your API key and model."
