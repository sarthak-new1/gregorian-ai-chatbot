import os
import streamlit as st
from dotenv import load_dotenv

# --- Load environment variables from .env ---
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not PINECONE_API_KEY or not OPENAI_API_KEY:
    print("WARNING: PINECONE_API_KEY or OPENAI_API_KEY not found in .env")

# Import AFTER env vars so agent.py sees keys
from agent import get_answer  # your LangChain + Pinecone agent


# --- Page config ---
st.set_page_config(
    page_title="Georgian AI Chatbot",
    layout="centered",
)

# --- Custom CSS for professional UI ---
st.markdown(
    """
<style>
/* Overall app background */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left, #e0e9ff 0, #f7f7ff 40%, #ffffff 100%);
}

/* Center content and limit width */
.block-container {
    max-width: 900px;
    padding-top: 2.5rem;
    padding-bottom: 2rem;
}

/* Hero header */
.hero-block {
    text-align: center;
    margin-bottom: 1.8rem;
}

/* Title: formal, legal-style serif font with deep navy color */
.main-title {
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 2.7rem;
    font-weight: 700;
    color: #0B2540;         /* <- updated professional navy */
    letter-spacing: 0.03em;
    margin-bottom: 0.4rem;
}

/* Subtitle */
.subheader {
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 1rem;
    color: #4b5563;
    margin-bottom: 0.3rem;
}

.hero-helper {
    font-size: 0.9rem;
    color: #6b7280;
    max-width: 520px;
    margin: 0 auto;
}

/* ... keep the rest of your CSS as-is ... */

/* Scrollable chat area */
.chat-scroll {
    max-height: 65vh;
    min-height: 40vh;
    overflow-y: auto;
    padding-right: 0.25rem;
    margin-bottom: 0.5rem;
    border-radius: 16px;
}

/* Custom scrollbar */
.chat-scroll::-webkit-scrollbar {
    width: 6px;
}
.chat-scroll::-webkit-scrollbar-track {
    background: transparent;
}
.chat-scroll::-webkit-scrollbar-thumb {
    background: #cbd5f5;
    border-radius: 999px;
}

/* Chat message spacing */
[data-testid="stChatMessage"] {
    padding-top: 0.1rem;
    padding-bottom: 0.1rem;
}

/* Buttons */
.stButton > button {
    border-radius: 999px;
    padding: 0.4rem 1rem;
    font-size: 0.9rem;
    border: none;
    background: #2563eb;
    color: #ffffff;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.28);
}
.stButton > button:hover {
    background: #1d4ed8;
}

/* Rounded input */
[data-testid="stTextInput"] input {
    border-radius: 999px;
    border: 1px solid #cbd5f5;
}

/* Input row */
.input-row {
    padding-top: 0.6rem;
    border-top: 1px solid #e5e7eb;
}

/* Footer */
.footer {
    font-size: 0.8rem;
    color: #9ca3af;
    margin-top: 0.6rem;
    text-align: center;
}

/* Helper text when chat is empty */
.helper-text {
    text-align: center;
    color: #9ca3af;
    margin-top: 1rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- Language & UI text setup (Georgian only) ---

LANG_GEORGIAN = "ka"
lang = LANG_GEORGIAN  # always Georgian

if "messages" not in st.session_state:
    # Each message: {"role": "user" or "assistant", "content": "..."}
    st.session_state.messages = []

TEXTS = {
    LANG_GEORGIAN: {
        "title": "Georgian AI Chatbot",
        "subtitle": "სპეციალიზირებული Georgian Legal AI ასისტენტი.",
        "hero_helper": " ",
        "send": "გაგზავნა",
        "placeholder": "შეიყვანეთ თქვენი კითხვა ან სამართლებრივი სიტუაცია...",
        "helper": "დაიწყეთ საუბარი Georgian AI ჩათბოტთან ქვემოთ მოცემული ველიდან.",
        "input_label": "შეტყობინება",
        "thinking": "ვფიქრობ...",
        "error": "დაფიქსირდა შეცდომა პასუხის მიღებისას. გთხოვთ, სცადოთ თავიდან.",
        "missing_keys": "API გასაღებები არ არის შემოწერილი (PINECONE_API_KEY / OPENAI_API_KEY).",
    }
}

t = TEXTS[lang]

# --- Header (centered hero section) ---
st.markdown(
    f"""
<div class="hero-block">
  <div class="main-title">{t['title']}</div>
  <div class="subheader">{t['subtitle']}</div>
  <div class="hero-helper">{t['hero_helper']}</div>
</div>
""",
    unsafe_allow_html=True,
)

if not PINECONE_API_KEY or not OPENAI_API_KEY:
    st.warning(t["missing_keys"])

# --- Scrollable chat area ---
chat_scroll = st.container()
with chat_scroll:
    st.markdown("<div class='chat-scroll'>", unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown(
            f"<div class='helper-text'>{t['helper']}</div>",
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state.messages:
            with st.chat_message("user" if msg["role"] == "user" else "assistant"):
                st.markdown(msg["content"])

    st.markdown("</div>", unsafe_allow_html=True)

# --- Input row (fixed below chat area) ---
st.markdown("<div class='input-row'>", unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    input_col1, input_col2 = st.columns([6, 1])

    with input_col1:
        user_input = st.text_input(
            label=t["input_label"],
            placeholder=t["placeholder"],
            label_visibility="collapsed",
        )
    with input_col2:
        submitted = st.form_submit_button(t["send"])

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown(
    "<div class='footer'>Georgian Legal AI · Powered by Pinecone & OpenAI</div>",
    unsafe_allow_html=True,
)

# --- Submit logic ---
if submitted and user_input.strip():
    user_text = user_input.strip()

    # 1) Store user message
    st.session_state.messages.append({"role": "user", "content": user_text})

    # 2) Get bot answer from agent
    try:
        if not PINECONE_API_KEY or not OPENAI_API_KEY:
            bot_reply = t["missing_keys"]
        else:
            with st.spinner(t["thinking"]):
                bot_reply = get_answer(user_text)
    except Exception:
        st.error(t["error"])
        bot_reply = t["error"]

    # 3) Store assistant message
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # 4) Rerun to refresh UI
    st.rerun()
