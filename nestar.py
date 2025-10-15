import streamlit as st
from transformers import pipeline
import re
import html

# ----------------------------- #
# App Configuration
# ----------------------------- #
st.set_page_config(page_title="NESTAR Messaging Filter", layout="wide")
st.markdown(
    """
    <style>
    body {
        background-color: #1e1e1e;
        color: white;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 20px;
    }
    .chat-bubble {
        padding: 10px 15px;
        border-radius: 10px;
        max-width: 75%;
        word-wrap: break-word;
        font-size: 16px;
        line-height: 1.4;
    }
    .incoming {
        background-color: #2e2e2e;
        align-self: flex-start;
    }
    .outgoing {
        background-color: #0078d4;
        align-self: flex-end;
        color: white;
    }
    .outgoing.flagged {
        background-color: #b91c1c;
        border-left: 4px solid red;
    }
    .name-label {
        font-weight: bold;
        font-size: 13px;
        margin-bottom: 3px;
        color: #aaaaaa;
    }
    .input-container {
        position: fixed;
        bottom: 20px;
        width: 100%;
        left: 0;
        padding: 10px 30px;
        background-color: #1e1e1e;
        box-shadow: 0 -1px 2px rgba(0,0,0,0.3);
    }
    .stTextInput > div > input {
        background-color: #2e2e2e;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("NESTAR Hate Crime Messaging Detection System")
st.caption("Microsoft Teams Simulation")

# ----------------------------- #
# Load Toxicity Classifier
# ----------------------------- #
@st.cache_resource
def load_model():
    return pipeline("text-classification", model="unitary/toxic-bert")

classifier = load_model()

# ----------------------------- #
# Keyword Detector
# ----------------------------- #
keyword_patterns = {
    "bitch": r"\b[b8][i1!|l*][t+][c(k)][h4]\b",
    "slut": r"\b[s5$][l1!][uü*][t+]\b",
    "whore": r"\b[wvv][h#][o0ö*][r][e3]\b",
    "gay is wrong": r"g[a@4]y\s+is\s+wrong"
}

def keyword_detector(text):
    lowered = text.lower()
    matched_keywords = []
    for keyword, pattern in keyword_patterns.items():
        if re.search(pattern, lowered):
            matched_keywords.append(keyword)
    if matched_keywords:
        return "toxic (keyword)", 1.0, matched_keywords
    else:
        return None, None, []

# ----------------------------- #
# Session State Setup
# ----------------------------- #
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------- #
# Display Chat History
# ----------------------------- #
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

# Initial system message
st.markdown("""
<div class="chat-bubble incoming">
    <div class="name-label">Alex:</div>
    Hi, how are you going?
</div>
""", unsafe_allow_html=True)

for msg in st.session_state.messages:
    st.markdown(msg, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------- #
# Input Form (Teams-style)
# ----------------------------- #
with st.form(key="chat_form"):
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    user_input = st.text_input("Type a message", value="", key="user_input", label_visibility="collapsed")
    submitted = st.form_submit_button("Send")
    st.markdown('</div>', unsafe_allow_html=True)

if submitted and user_input.strip():
    label, score, matched_keywords = keyword_detector(user_input)
    bubble_class = "chat-bubble outgoing"
    bubble_note = ""
    safe_input = html.escape(user_input)

    if label == "toxic (keyword)":
        bubble_class += " flagged"
        bubble_note = f"""<div style='font-style: italic; font-size: 13px; margin-top: 5px;'>*This message was flagged for hate speech and was not sent.*</div>"""
    else:
        result = classifier(user_input)[0]
        label = result['label'].lower()
        score = result['score']
        if label in ["toxic", "hate", "offensive"] and score >= 0.85:
            bubble_class += " flagged"
            bubble_note = f"""<div style='font-style: italic; font-size: 13px; margin-top: 5px;'>*Flagged by AI (confidence: {score:.2f}). Not sent.*</div>"""

    # Construct message bubble
    message_html = f"""
    <div class="{bubble_class}">
        <div class="name-label">You:</div>
        {safe_input}
        {bubble_note}
    </div>
    """

    # Add to session and clear input
    st.session_state.messages.append(message_html)
    st.session_state.user_input = ""
    st.rerun()
