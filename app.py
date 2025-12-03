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

# --- Background image URL ---
BACKGROUND_IMAGE_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/"
    "The_Supreme_Court_of_Georgia_is_located_at_the_Nathan_Deal_Judicial_Center_in_Atlanta.jpg/"
    "640px-The_Supreme_Court_of_Georgia_is_located_at_the_Nathan_Deal_Judicial_Center_in_Atlanta.jpg"
)

# --- Page config ---
st.set_page_config(
    page_title="Georgian AI Chatbot",
    layout="centered",
)

# --- Custom CSS for professional UI with background image ---
st.markdown(
    f"""
<style>
/* Overall app background: image + dark overlay for contrast */
[data-testid="stAppViewContainer"] {{
    background-image:
        linear-gradient(135deg, rgba(8, 14, 29, 0.92), rgba(15, 23, 42, 0.92)),
        url("{BACKGROUND_IMAGE_URL}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

[data-testid="stAppViewContainer"] * {{
    color: #e5e7eb;
}}

.block-container {{
    max-width: 900px;
    padding-top: 2.5rem;
    padding-bottom: 2.5rem;
}}


/* Hero header */
.hero-block {{
    text-align: center;
    margin-bottom: 1.6rem;
}}

.main-title {{
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #f9fafb;
    letter-spacing: 0.03em;
    margin-bottom: 0.3rem;
}}

.subheader {{
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 1rem;
    color: #d1d5db;
    margin-bottom: 0.4rem;
}}

.hero-helper {{
    font-size: 0.9rem;
    color: #9ca3af;
    max-width: 520px;
    margin: 0 auto;
}}


.chat-scroll {{
    max-height: 65vh;
    min-height: 40vh;
    overflow-y: auto;
    padding-right: 0.35rem;
    margin-bottom: 0.2rem;
    border-radius: 16px;
}}

/* Custom scrollbar */
.chat-scroll::-webkit-scrollbar {{
    width: 6px;
}}
.chat-scroll::-webkit-scrollbar-track {{
    background: transparent;
}}
.chat-scroll::-webkit-scrollbar-thumb {{
    background: #4b5563;
    border-radius: 999px;
}}

/* Chat messages */
[data-testid="stChatMessage"] {{
    padding-top: 0.15rem;
    padding-bottom: 0.15rem;
}}

[data-testid="stChatMessage"] > div {{
    background: rgba(17, 24, 39, 0.95) !important;
    border-radius: 16px !important;
    padding: 0.7rem 0.9rem !important;
    border: 1px solid rgba(75, 85, 99, 0.6);
}}

/* Buttons */
.stButton > button {{
    border-radius: 999px;
    padding: 0.4rem 1rem;
    font-size: 0.9rem;
    border: none;
    background: #2563eb;
    color: #ffffff;
    font-weight: 500;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
}}
.stButton > button:hover {{
    background: #1d4ed8;
}}

/* Rounded input */
[data-testid="stTextInput"] input {{
    border-radius: 999px;
    border: 1px solid rgba(148, 163, 184, 0.7);
    background: rgba(15, 23, 42, 0.9);
    color: #e5e7eb;
}}
[data-testid="stTextInput"] input::placeholder {{
    color: #6b7280;
}}

/* Input row */
.input-row {{
    padding-top: 0.6rem;
    margin-top: 0.4rem;
    border-top: 1px solid rgba(55, 65, 81, 0.8);
}}

/* Footer */
.footer {{
    font-size: 0.75rem;
    color: #6b7280;
    margin-top: 0.75rem;
    text-align: center;
}}

/* Helper text when chat is empty */
.helper-text {{
    text-align: center;
    color: #9ca3af;
    margin-top: 1rem;
}}

/* Remove default Streamlit header/menu spacing and background */
[data-testid="stHeader"], [data-testid="stToolbar"] {{
    background: transparent;
}}
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

st.markdown("</div>", unsafe_allow_html=True)  # close input-row

# Footer
st.markdown(
    "<div class='footer'> </div>",
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
