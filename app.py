import os
import streamlit as st
from groq import Groq

# Page Setup
st.set_page_config(
    page_title="Cinetrend | AI Movie Recommender",
    page_icon="🎬",
    layout="centered"
)

# Custom Styling for polished look
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #888888;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎬 Cinetrend Recommender</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Discover your next favorite movie powered by high-speed Groq AI</div>', unsafe_allow_html=True)

# API Key Retrieval (Prioritizes Secrets -> Fallback)
api_key = None
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
elif os.environ.get("GROQ_API_KEY"):
    api_key = os.environ.get("GROQ_API_KEY")
else:
    api_key = "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"

client = Groq(api_key=api_key)

# Input UI
with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        user_query = st.text_input(
            "Favorite movie, vibe, or plot idea:",
            placeholder="e.g., Mind-bending sci-fi like Interstellar or Dark",
            help="Type anything you want: genre, actors, plot twists, or emotional vibe."
        )
    with col2:
        mood = st.selectbox(
            "Current Mood:",
            ["Any Mood", "Mind-bending & Mystery", "Cozy & Feel-Good", "Thrilling & Edge-of-Seat", "Dark & Gritty", "Heartfelt & Emotional"]
        )

    recommend_button = st.button("✨ Get Recommendations", type="primary")

# Recommendation Execution
if recommend_button:
    if not user_query.strip():
        st.warning("Please enter a movie title, theme, or plot vibe first!")
    else:
        with st.spinner("Analyzing cinema trends & curation..."):
            try:
                system_prompt = (
                    "You are a world-class film critic and personalized cinema recommender. "
                    "Recommend exactly 3 to 4 perfectly matched movies. "
                    "For each movie, strictly provide: "
                    "1. Title (Release Year) with Genre "
                    "2. One-sentence Logline/Hook "
                    "3. Why it matches the user's taste "
                    "Keep tone sharp, engaging, and formatting concise. Do not exceed 500 words."
                )

                user_prompt = f"User preference: '{user_query}'. Mood: '{mood}'."

                # High-throughput model + safety token cap
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=650,
                    temperature=0.6,
                )

                st.success("Here are your curated recommendations:")
                st.markdown(response.choices[0].message.content)

            except Exception as e:
                error_text = str(e)
                if "429" in error_text:
                    st.error("Traffic is high right now. Please wait 10-15 seconds and click again!")
                else:
                    st.error(f"Error generating recommendations: {error_text}")

st.divider()
st.caption("Built with Streamlit & Groq Cloud Engine | Cinetrend")