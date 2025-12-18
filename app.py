import streamlit as st
from groq import Groq
from textblob import TextBlob
import pandas as pd
import os

# ------------------ API SETUP ------------------
client = Groq(
    api_key="API_KEY_PLACEHOLDER"  # Replace with your actual API key
)


def generate_response(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a mental health support chatbot. "
                        "Be supportive, calm, and give general mental health tips. "
                        "Do not give medical diagnosis."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"DEBUG ERROR: {e}"


def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity

    if polarity > 0.5:
        return "Very Positive", polarity
    elif 0.1 < polarity <= 0.5:
        return "Positive", polarity
    elif -0.1 <= polarity <= 0.1:
        return "Neutral", polarity
    elif -0.5 < polarity < -0.1:
        return "Negative", polarity
    else:
        return "Very Negative", polarity

# ------------------ COPING STRATEGIES ------------------
def provide_coping_strategy(sentiment):
    strategies = {
        "Very Positive": "Keep nurturing these positive feelings. Share your joy with others.",
        "Positive": "You're doing well. Try journaling or gratitude exercises.",
        "Neutral": "Neutral moods are okay. Light exercise or music may help.",
        "Negative": "Try deep breathing or talking to someone you trust.",
        "Very Negative": "You are not alone. Please consider reaching out to a trusted person or professional."
    }
    return strategies.get(sentiment, "Take care of yourself.")

# ------------------ DISCLAIMER ------------------
def display_disclaimer():
    st.sidebar.markdown(
        "<h3 style='color:red;'>Data Privacy Disclaimer</h3>",
        unsafe_allow_html=True
    )
    st.sidebar.write(
        "Messages are used only during this session and not stored permanently. "
        "Avoid sharing sensitive personal information."
    )

# ------------------ STREAMLIT UI ------------------
st.title("🧠 Mental Health Support Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mood_tracker" not in st.session_state:
    st.session_state.mood_tracker = []

with st.form("chat_form"):
    user_message = st.text_input("You:")
    submit = st.form_submit_button("Send")

if submit and user_message:
    st.session_state.messages.append(("You", user_message))

    sentiment, polarity = analyze_sentiment(user_message)
    coping_strategy = provide_coping_strategy(sentiment)
    response = generate_response(user_message)

    st.session_state.messages.append(("Bot", response))
    st.session_state.mood_tracker.append((user_message, sentiment, polarity))

# Display chat
for sender, msg in st.session_state.messages:
    st.write(f"**{sender}:** {msg}")

# Mood chart
if st.session_state.mood_tracker:
    df = pd.DataFrame(
        st.session_state.mood_tracker,
        columns=["Message", "Sentiment", "Polarity"]
    )
    st.line_chart(df["Polarity"])

# Coping suggestion
if submit:
    st.info(f"Suggested Coping Strategy: {coping_strategy}")

# Resources
st.sidebar.title("Emergency Resources")
st.sidebar.write(
    "If you feel unsafe, please contact local emergency services or a trusted adult."
)

display_disclaimer()
