import streamlit as st
from groq import Groq
from textblob import TextBlob
import pandas as pd
from fpdf import FPDF
import os

# ------------------ API SETUP ------------------
client = Groq(
    api_key="API_KEY_PLACEHOLDER"  # Replace with your actual API key
)

# ------------------ AI RESPONSE ------------------
def generate_response(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a mental health support chatbot. "
                        "Be calm, kind, supportive, and give general mental wellness tips. "
                        "Do NOT give medical diagnosis or emergency advice."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# ------------------ SENTIMENT ------------------
def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity

    if polarity > 0.5:
        return "Very Positive", polarity
    elif polarity > 0.1:
        return "Positive", polarity
    elif polarity >= -0.1:
        return "Neutral", polarity
    elif polarity > -0.5:
        return "Negative", polarity
    else:
        return "Very Negative", polarity

# ------------------ COPING STRATEGY ------------------
def coping_strategy(sentiment):
    return {
        "Very Positive": "Keep nurturing positive habits.",
        "Positive": "Gratitude journaling can help.",
        "Neutral": "Light exercise or music may improve mood.",
        "Negative": "Deep breathing or talking to a trusted person may help.",
        "Very Negative": "You are not alone. Reach out to someone you trust."
    }.get(sentiment, "Take care of yourself.")

# ------------------ PDF GENERATION ------------------
def create_pdf(user_text, bot_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Mental Health Chatbot Response", ln=True)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, f"\nUser Query:\n{user_text}\n\nAI Response:\n{bot_text}")

    file_path = "chat_response.pdf"
    pdf.output(file_path)
    return file_path

# ------------------ UI ------------------
st.set_page_config(page_title="Mental Health Support Chatbot", layout="centered")
st.title("🧠 Mental Health-AI   Support Chatbot")

if "history" not in st.session_state:
    st.session_state.history = []

if "mood" not in st.session_state:
    st.session_state.mood = []

user_input = st.text_input("How are you feeling today?")

if st.button("Get Support") and user_input:
    bot_reply = generate_response(user_input)
    sentiment, polarity = analyze_sentiment(user_input)

    st.session_state.history.append(("You", user_input))
    st.session_state.history.append(("Bot", bot_reply))
    st.session_state.mood.append(polarity)

    st.subheader("🤖 AI Response")
    st.write(bot_reply)

    st.info(f"Sentiment: **{sentiment}**")
    st.success(coping_strategy(sentiment))

    pdf_file = create_pdf(user_input, bot_reply)
    with open(pdf_file, "rb") as f:
        st.download_button(
            label="📄 Download Response as PDF",
            data=f,
            file_name="mental_health_response.pdf",
            mime="application/pdf"
        )

# ------------------ CHAT HISTORY ------------------
if st.session_state.history:
    st.subheader("🗂 Chat History")
    for sender, msg in st.session_state.history:
        st.write(f"**{sender}:** {msg}")

# ------------------ MOOD CHART ------------------
if st.session_state.mood:
    st.subheader("📊 Mood Tracker")
    df = pd.DataFrame(st.session_state.mood, columns=["Polarity"])
    st.line_chart(df)

# ------------------ DISCLAIMER ------------------
st.sidebar.warning(
    "⚠️ This chatbot is for educational purposes only.\n\n"
    "If you feel unsafe, please contact a trusted adult or local emergency services."
)
