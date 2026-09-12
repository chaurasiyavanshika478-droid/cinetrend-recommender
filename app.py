import os
import streamlit as st
from groq import Groq

# Page Configuration
st.set_page_config(
    page_title="CineTrend & Melodies AI",
    page_icon="🎬",
    layout="centered"
)

# Dark Theme UI Styling
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e2337 0%, #0d0f17 100%);
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    h1 {
        font-weight: 800 !important;
        background: linear-gradient(90deg, #f87171, #fb923c, #facc15);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stTextInput > div > div > input {
        background-color: #1e2235 !important;
        color: #ffffff !important;
        border: 1.5px solid #3b4261 !important;
        border-radius: 10px !important;
        padding: 12px 14px !important;
    }
    
    div[data-testid="stHorizontalBlock"] .stButton > button {
        background: #1e2438 !important;
        color: #e2e8f0 !important;
        border: 1px solid #475569 !important;
        border-radius: 18px !important;
        padding: 6px 12px !important;
        font-size: 13px !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        background: #f87171 !important;
        color: #ffffff !important;
        border-color: #f87171 !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 10px 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# Safe API Key Loading (Local + Streamlit Cloud)
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        api_key = None

if not api_key:
    api_key = "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"

client = Groq(api_key=api_key)

# Header Section
st.title("CineTrend & Melodies")
st.caption("AI-Powered Discovery for Bollywood Tracks & Cinema")

# Session State for Mood Pills
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "trigger_search" not in st.session_state:
    st.session_state.trigger_search = False

# Quick Pick Pills
st.markdown("<p style='color:#94a3b8; font-size:13px; font-weight:600; text-transform:uppercase; margin-bottom:8px;'>Quick Picks</p>", unsafe_allow_html=True)
pills = [
    ("🌙 Late Night Lofi", "Late Night Lofi Bollywood"),
    ("🌧️ Rainy Nostalgia", "Rainy Day 90s Romance"),
    ("💔 Arijit Melodies", "Arijit Singh Heartbreak Melodies"),
    ("⚡ Energetic Beats", "High Energy Bollywood Dance Hits"),
    ("🕵️ Plot Twist Movies", "Mind Bending Bollywood Mystery Thrillers")
]

cols = st.columns(len(pills))
for idx, (label, val) in enumerate(pills):
    if cols[idx].button(label, key=f"pill_{idx}", use_container_width=True):
        st.session_state.search_query = val
        st.session_state.trigger_search = True
        st.rerun()

# Search Box
user_input = st.text_input(
    "Search any artist, vibe, or movie plot:",
    value=st.session_state.search_query,
    placeholder="e.g. KK, Mohit Chauhan, Drishyam, 2000s nostalgic songs...",
    key="main_input"
)

# Preferences
col_cat, col_count = st.columns([2, 1])
with col_cat:
    recommend_type = st.radio(
        "Category:",
        ["🎵 Bollywood Tracks", "🎬 Feature Movies"],
        horizontal=True
    )

with col_count:
    num_items = st.slider("Results", min_value=2, max_value=5, value=3)

# Search Execution
search_clicked = st.button("Search ✨", type="primary", use_container_width=True)

if search_clicked or st.session_state.trigger_search:
    st.session_state.trigger_search = False
    active_query = user_input.strip() if user_input.strip() else st.session_state.search_query

    if not active_query:
        st.warning("Please type a singer, movie name, or click a pill above!")
    else:
        with st.spinner("Analyzing vibe & curating recommendations..."):
            prompt = f"""
            User Query: '{active_query}'
            Category: {recommend_type}
            Count: {num_items}

            GUIDELINES:
            1. TYPO HANDLING: Correct typos automatically (e.g. 'arjti' -> 'Arijit Singh').
            2. RELEVANCE CHECK: If input is gibberish, say: '⚠️ No match found. Try an artist name like KK or a vibe like Retro.'
            3. FOR SONGS:
               - **Title** (Movie/Album, Year)
               - **Artists**: Singers | Music Director
               - **Vibe**: 1 concise line
               - **Listen**: [▶ Listen on YouTube](https://www.youtube.com/results?search_query={active_query})
            4. FOR MOVIES:
               - **Title** (Year) • Genre
               - **Why Watch**: 1 crisp sentence
               - **Streaming**: Netflix / Prime / JioCinema / Hotstar
            Keep formatting clean with bullet points and bold headers. No conversational opening or closing text.
            """

            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model="qwen/qwen3.8-27b",
                )
                
                result = chat_completion.choices[0].message.content
                st.markdown("---")
                st.markdown(result)
            except Exception as e:
                st.error(f"Error: {e}")