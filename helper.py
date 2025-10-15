import requests
import streamlit as st

API_KEY = st.secrets["OPENROUTER_API_KEY"]
MODEL = "gpt-4o-mini"

def get_personalized_answer(question, mbti, learning_style, language="en"):
    if not question.strip():
        return "Please enter a valid question."

    if language == "hi":
        prompt = f"""
        आप एक विशेषज्ञ शिक्षक हैं जो छात्रों की MBTI व्यक्तित्व और सीखने की शैली को समझते हैं।
        छात्र की MBTI प्रकार है {mbti} और उसकी सीखने की शैली है {learning_style}।
        इस प्रश्न का उत्तर छात्रों के स्तर पर, आसान भाषा में और विस्तार से दें:

        प्रश्न: {question}
        """
    else:
        prompt = f"""
        You are an expert teacher who adapts explanations according to the student's MBTI type and learning style.
        The student's MBTI is {mbti}, and their learning style is {learning_style}.
        Answer the following question in detail, easy-to-understand language:

        Question: {question}
        """

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful AI study assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        st.error("⚠️ Error generating answer:")
        st.write(str(e))
        if "response" in locals():
            st.write("Raw API response:", response.text)
        return "Sorry, something went wrong. Please check your API key or try again."
