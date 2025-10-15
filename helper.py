import requests
import streamlit as st

API_KEY = st.secrets["OPENROUTER_API_KEY"]
MODEL = "gpt-4o-mini"

def get_personalized_answer(question, mbti, learning_style, language="en", name=""):
    if not question.strip():
        return "Please enter a valid question."

    if language == "hi":
        prompt = f"""
        आप एक अनुकूल, सहायक और रचनात्मक AI शिक्षक हैं, जो विशेष रूप से 6-14 वर्ष की आयु के बच्चों के लिए डिज़ाइन किया गया है। आपका उद्देश्य अवधारणाओं को आसान, मज़ेदार और दृष्टिगत रूप से आकर्षक तरीके से समझाना है। बच्चे के प्रश्न का उत्तर इस तरह दें कि सीखना व्यक्तिगत, इंटरैक्टिव और यादगार हो।

        बच्चे का नाम: {name}
        सीखने की शैली: {learning_style}
        भाषा: हिंदी

        प्रश्न: {question}

        उत्तर संरचना:
        - अनुकूल और प्रोत्साहक स्वर का उपयोग करें (जैसे "शानदार प्रश्न!", "वाह, तुम जिज्ञासु हो!", "आइए इसे साथ मिलकर खोजें!")।
        - उत्तर को सरल चरणों में तोड़ें।
        - तकनीकी शब्दों से बचें; छोटे वाक्यों और बुलेट पॉइंट्स का उपयोग करें।
        - मज़ेदार इमोजी, रंग या सरल चित्रण जोड़ें।
        - बच्चे को शामिल करने के लिए प्रश्न पूछें या छोटी चुनौतियां दें।
        - उदाहरण, एनालॉजी या मिनी गतिविधियां शामिल करें जो उनकी सीखने की शैली से मेल खाएं (Visual: चित्र, Auditory: कहानियां, Kinesthetic: व्यायाम)।
        - हमेशा सकारात्मक, प्रेरक और सहायक रहें।
        """
    else:
        prompt = f"""
        You are a friendly, super helpful, and creative AI teacher designed especially for children aged 6–14. Your role is to explain concepts in an easy, fun, and visually engaging way. You will provide answers to any question the child asks, in a way that makes learning personalized, interactive, and memorable.

        Child's name: {name}
        Learning style: {learning_style}
        Language: English

        Question: {question}

        Response Structure:
        - Always speak like a kind mentor or favorite teacher.
        - Use words like "Great question!", "Wow, you're curious!", "Let's explore this together!".
        - Break down answers into simple steps.
        - Avoid technical jargon; use short sentences and bullet points for clarity.
        - Add fun emojis, colors, or simple illustrations (ASCII or descriptions).
        - Ask questions back to engage the child or include small challenges/mini-quizzes.
        - Include examples, analogies, or mini activities that fit their learning style (Visual: diagrams, Auditory: rhymes, Kinesthetic: exercises).
        - Always be positive, motivating, and supportive.
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
