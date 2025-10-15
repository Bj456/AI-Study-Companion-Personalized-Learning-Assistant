import openai
import streamlit as st

# ✅ Load API key securely from Streamlit Secrets
openai.api_key = st.secrets["OPENROUTER_API_KEY"]
openai.base_url = "https://openrouter.ai/api/v1"

def get_personalized_answer(question, mbti, learning_style, language="en"):
    # --- Build prompt dynamically ---
    if language == "hi":
        user_prompt = f"""
        आप एक विशेषज्ञ शिक्षक हैं जो छात्रों की MBTI व्यक्तित्व और सीखने की शैली को समझते हैं।
        छात्र की MBTI प्रकार है {mbti} और उसकी सीखने की शैली है {learning_style}।
        इस प्रश्न का उत्तर छात्रों के स्तर पर, आसान भाषा में और विस्तार से दें:
        {question}
        """
    else:
        user_prompt = f"""
        You are an expert teacher who adapts explanations according to the student's MBTI type and learning style.
        The student's MBTI is {mbti}, and their learning style is {learning_style}.
        Give a detailed, easy-to-understand answer for the question:
        {question}
        """

    # --- Make API call safely ---
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # works on OpenRouter
            messages=[
                {"role": "system", "content": "You are a helpful AI study assistant."},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )

        # --- Safe universal content extraction ---
        content = None

        if hasattr(response.choices[0], "message"):
            msg = response.choices[0].message
            if isinstance(msg, dict):
                content = msg.get("content", None)
            elif hasattr(msg, "content"):
                content = msg.content
        elif hasattr(response.choices[0], "text"):
            content = response.choices[0].text
        else:
            # fallback for new API schema
            content = response.choices[0].get("message", {}).get("content", None)

        if not content:
            raise ValueError("No content field found in response.")

        return content.strip()

    except Exception as e:
        # Print full details in Streamlit console
        st.error("⚠️ An error occurred while generating the answer.")
        st.write("**Error Type:**", type(e).__name__)
        st.write("**Error Message:**", str(e))
        if "response" in locals():
            st.write("**Raw API Response:**", response)
        return "Sorry, something went wrong while generating the answer."
