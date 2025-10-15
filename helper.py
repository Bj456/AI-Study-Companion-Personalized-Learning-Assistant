import openai
import os

# ✅ Use OpenRouter API instead of OpenAI
openai.api_key = os.getenv("OPENROUTER_API_KEY") or "YOUR_OPENROUTER_API_KEY"
openai.base_url = "https://openrouter.ai/api/v1"

def get_personalized_answer(question, mbti, learning_style, language="en"):
    # 🧠 Create prompt according to language
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

    # 🧩 Call OpenRouter API
    response = openai.chat.completions.create(
        model="openai/gpt-4o-mini",  # you can replace this with any model from OpenRouter
        messages=[
            {"role": "system", "content": "You are a helpful AI study assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content
