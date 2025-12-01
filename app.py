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
    background: linear-gradient(180deg, #e5edff 0%, #f4f5fb 40%, #fdfdfd 100%);
}

/* Center content and limit width */
.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Title styling */
.main-title {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    text-align: left;
    color: #111827;
    margin-bottom: 0.25rem;
}

.subheader {
    font-size: 0.9rem;
    color: #6b7280;
    margin-bottom: 1.5rem;
}

/* Scrollable chat area */
.chat-scroll {
    max-height: 65vh;
    min-height: 40vh;
    overflow-y: auto;
    padding-right: 0.25rem;
    margin-bottom: 0.5rem;
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

/* Style all buttons a bit more modern */
.stButton > button {
    border-radius: 999px;
    padding: 0.35rem 0.9rem;
    font-size: 0.9rem;
    border: none;
    background: #2563eb;
    color: #ffffff;
    font-weight: 500;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);
}
.stButton > button:hover {
    background: #1d4ed8;
}

/* Make text input a bit rounded */
[data-testid="stTextInput"] input {
    border-radius: 999px;
    border: 1px solid #cbd5f5;
}

/* Input row styling */
.input-row {
    padding-top: 0.5rem;
    border-top: 1px solid #e5e7eb;
}

/* Footer */
.footer {
    font-size: 0.8rem;
    color: #9ca3af;
    margin-top: 0.35rem;
    text-align: right;
}

/* Language toggle alignment */
.lang-toggle-container {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-top: 0.25rem;
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

# --- Language & UI text setup ---

LANG_GEORGIAN = "ka"
LANG_ENGLISH = "en"

if "lang" not in st.session_state:
    st.session_state.lang = LANG_GEORGIAN

if "messages" not in st.session_state:
    # Each message: {"role": "user" or "assistant", "content": "..."}
    st.session_state.messages = []

lang = st.session_state.lang

TEXTS = {
    LANG_GEORGIAN: {
        "title": "Georgian AI Chatbot",
        "subtitle": "სპეციალიზირებული Georgian Legal AI ასისტენტი.",
        "send": "გაგზავნა",
        "placeholder": "შეიყვანეთ თქვენი შეტყობინება...",
        "language_toggle_label": "🇬🇪 / 🇬🇧",
        "helper": "დაიწყეთ საუბარი Georgian AI ჩათბოტთან ქვემოთ მოცემული ველიდან.",
        "input_label": "შეტყობინება",
        "thinking": "ვფიქრობ...",
        "error": "დაფიქსირდა შეცდომა პასუხის მიღებისას. გთხოვთ, სცადოთ თავიდან.",
        "missing_keys": "API გასაღებები არ არის შემოწერილი (PINECONE_API_KEY / OPENAI_API_KEY).",
    },
    LANG_ENGLISH: {
        "title": "Georgian AI Chatbot",
        "subtitle": "Specialized Georgian legal AI assistant.",
        "send": "Send",
        "placeholder": "Type your message...",
        "language_toggle_label": "🇬🇧 / 🇬🇪",
        "helper": "Start chatting with the Georgian AI chatbot using the box below.",
        "input_label": "Message",
        "thinking": "Thinking...",
        "error": "An error occurred while getting the answer. Please try again.",
        "missing_keys": "API keys are missing (PINECONE_API_KEY / OPENAI_API_KEY).",
    },
}


def toggle_language():
    if st.session_state.lang == LANG_GEORGIAN:
        st.session_state.lang = LANG_ENGLISH
    else:
        st.session_state.lang = LANG_GEORGIAN


# --- Header: title + language toggle ---

header_col1, header_col2 = st.columns([4, 1])

with header_col1:
    st.markdown(
        f"<div class='main-title'>{TEXTS[lang]['title']}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='subheader'>{TEXTS[lang]['subtitle']}</div>",
        unsafe_allow_html=True,
    )

with header_col2:
    st.markdown("<div class='lang-toggle-container'>", unsafe_allow_html=True)
    if st.button(TEXTS[lang]["language_toggle_label"]):
        toggle_language()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Refresh lang after possible rerun
lang = st.session_state.lang

if not PINECONE_API_KEY or not OPENAI_API_KEY:
    st.warning(TEXTS[lang]["missing_keys"])

st.markdown("")  # spacing


# Scrollable chat area
chat_scroll = st.container()
with chat_scroll:
    st.markdown("<div class='chat-scroll'>", unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown(
            f"<div class='helper-text'>{TEXTS[lang]['helper']}</div>",
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state.messages:
            with st.chat_message("user" if msg["role"] == "user" else "assistant"):
                # Show content as Markdown (so model can format, but no raw HTML wrapper from us)
                st.markdown(msg["content"])

    st.markdown("</div>", unsafe_allow_html=True)

# --- Input row (fixed below chat area) ---
st.markdown("<div class='input-row'>", unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    input_col1, input_col2 = st.columns([6, 1])

    with input_col1:
        user_input = st.text_input(
            label=TEXTS[lang]["input_label"],
            placeholder=TEXTS[lang]["placeholder"],
            label_visibility="collapsed",
        )
    with input_col2:
        submitted = st.form_submit_button(TEXTS[lang]["send"])

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
            bot_reply = TEXTS[lang]["missing_keys"]
        else:
            with st.spinner(TEXTS[lang]["thinking"]):
                bot_reply = get_answer(user_text)
    except Exception:
        st.error(TEXTS[lang]["error"])
        bot_reply = TEXTS[lang]["error"]

    # 3) Store assistant message
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # 4) Rerun to refresh UI
    st.rerun()
