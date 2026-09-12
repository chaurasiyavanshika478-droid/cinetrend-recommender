import json
import os
import urllib.parse
import streamlit as st
from groq import Groq

# 1. Page Configuration
st.set_page_config(page_title="VibeMatch | Movies & Songs", page_icon="✨", layout="centered")

st.markdown("<h2 style='text-align: center;'>✨ VibeMatch</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Pick your vibe, get instant movies or songs with direct listen/watch links.</p>", unsafe_allow_html=True)

# 2. Safe API Key Retrieval (No StreamlitSecretNotFoundError)
api_key = None
try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.environ.get("GROQ_API_KEY") or "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"

# Initialize Client
client = Groq(api_key=api_key)

# 3. UI Inputs
category = st.radio(
    "What do you want to explore?",
    options=["🎬 Movies", "🎵 Songs"],
    horizontal=True
)

col1, col2 = st.columns([2, 1])

with col1:
    user_input = st.text_input(
        "Any specific tastes? (Optional)",
        placeholder="e.g. Arijit Singh vibe, sci-fi thriller, 90s rock..."
    )

with col2:
    vibe = st.selectbox(
        "Mood / Vibe:",
        [
            "🌧️ Rainy Day",
            "💔 Sad & Emotional",
            "🌙 Late Night Chill",
            "☕ Cozy & Warm",
            "❤️ Romantic",
            "⚡ Hype & Party",
            "🧘 Calm & Relax"
        ]
    )

find_btn = st.button("✨ Get Recommendations", type="primary", use_container_width=True)

# 4. Recommendation Generation with Dynamic Links
if find_btn:
    with st.spinner("Curating your picks..."):
        try:
            is_movie = "Movies" in category

            if is_movie:
                system_prompt = (
                    "You are a movie recommendation assistant. "
                    "Return ONLY a valid JSON array containing exactly 3 items. No markdown wrapper, no extra conversational text. "
                    "Schema: [{\"title\": \"Movie Title\", \"year\": \"2021\", \"genre\": \"Sci-Fi\", \"hook\": \"One line summary\", \"why\": \"Why it fits the mood\"}]"
                )
            else:
                system_prompt = (
                    "You are a music recommendation assistant. "
                    "Return ONLY a valid JSON array containing exactly 3 items. No markdown wrapper, no extra conversational text. "
                    "Schema: [{\"title\": \"Song Title\", \"artist\": \"Artist Name\", \"genre\": \"Indie Pop\", \"hook\": \"Highlight of the track\", \"why\": \"Why it fits the mood\"}]"
                )

            user_prompt = f"Category: {category}\nVibe: {vibe}\nUser Preferences: {user_input if user_input else 'None'}"

            response = client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=450
            )

            raw_text = response.choices[0].message.content.strip()

            # Clean markdown code blocks if the model outputs them
            if "```" in raw_text:
                parts = raw_text.split("```")
                raw_text = parts[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            raw_text = raw_text.strip()

            items = json.loads(raw_text)

            st.markdown("---")

            # Render Cards with Direct Links
            for item in items:
                if is_movie:
                    title_line = f"🎬 **{item.get('title')}** ({item.get('year')}) — *{item.get('genre')}*"
                    search_query = f"{item.get('title')} {item.get('year')} trailer"
                    encoded_query = urllib.parse.quote_plus(search_query)

                    yt_link = f"https://www.youtube.com/results?search_query={encoded_query}"
                    google_link = f"https://www.google.com/search?q={urllib.parse.quote_plus(item.get('title') + ' movie where to watch')}"

                    st.markdown(title_line)
                    st.write(f"**Story:** {item.get('hook')}")
                    st.write(f"**Vibe Match:** {item.get('why')}")
                    st.markdown(f"[▶️ Watch Trailer on YouTube]({yt_link}) &nbsp;|&nbsp; [🍿 Where to Stream]({google_link})")
                else:
                    title_line = f"🎵 **{item.get('title')}** by *{item.get('artist')}* — *{item.get('genre')}*"
                    search_query = f"{item.get('title')} {item.get('artist')}"
                    encoded_query = urllib.parse.quote_plus(search_query)

                    spotify_link = f"https://open.spotify.com/search/{encoded_query}"
                    yt_link = f"https://www.youtube.com/results?search_query={encoded_query}"

                    st.markdown(title_line)
                    st.write(f"**Vibe:** {item.get('hook')}")
                    st.write(f"**Why it fits:** {item.get('why')}")
                    st.markdown(f"[🟢 Play on Spotify]({spotify_link}) &nbsp;|&nbsp; [▶️ Play on YouTube]({yt_link})")

                st.divider()

        except Exception as e:
            st.error(f"Could not load formatted links: {e}")