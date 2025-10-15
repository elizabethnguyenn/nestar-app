import streamlit as st
from transformers import pipeline
import re
import html
import os

os.environ['TRANSFORMERS_CACHE'] = './model_cache'

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(page_title="NESTAR Messaging Filter", layout="centered")
st.title("NESTAR Hate Crime Messaging Detection System")
st.caption("Microsoft Teams Simulation")

# -----------------------------
# Custom CSS for MS Teams style
# -----------------------------
st.markdown("""
<style>
/* Chat container */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 80px;
}

/* Bubble styles */
.chat-bubble {
    padding: 10px 15px;
    border-radius: 15px;
    max-width: 75%;
    word-wrap: break-word;
    font-size: 16px;
    position: relative;
}

.incoming {
    background-color: #f1f1f1;
    align-self: flex-start;
    margin-left: 10px;
}

.outgoing {
    background-color: #cce4f7;
    align-self: flex-end;
    margin-right: 10px;
}

.outgoing.flagged {
    background-color: #ffebee;
    border-left: 5px solid red;
}

.name-label {
    font-weight: bold;
    font-size: 13px;
    margin-bottom: 3px;
    color: #555;
}

/* Message bar (like Teams) */
.message-input {
    position: fixed;
    bottom: 15px;
    left: 0;
    width: 100%;
    padding: 10px 20px;
    background-color: white;
    border-top: 1px solid #ddd;
}

.message-input input {
    width: 90%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 8px;
}

.message-input button {
    padding: 10px 20px;
    background-color: #0078d4;
    color: white;
    border: none;
    border-radius: 8px;
    margin-left: 10px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Load Toxicity Classifier
# -----------------------------
@st.cache_resource
def load_model():
    return pipeline("text-classification", model="unitary/toxic-bert")

classifier = load_model()

# -----------------------------
# Keyword Pattern Detection
# -----------------------------
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

# -----------------------------
# Session State for Messages
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# Display Previous Messages
# -----------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Static incoming message (Alex)
st.markdown("""
    <div class="chat-bubble incoming">
        <div class="name-label">Alex:</div>
        Hi, how are you going?
    </div>
""", unsafe_allow_html=True)

# Show user message history
for msg_html in st.session_state.messages:
    st.markdown(msg_html, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Message Input Area
# -----------------------------
with st.form(key="chat_form"):
    user_input = st.text_input("", value="", placeholder="Type a message...", key="user_message")
    submitted = st.form_submit_button("Send Message")

if submitted and user_input.strip():
    label, score, matched_keywords = keyword_detector(user_input)
    bubble_class = "chat-bubble outgoing"
    bubble_note = ""
    safe_input = html.escape(user_input)

    # Keyword-based flagging
    if label == "toxic (keyword)":
        bubble_class += " flagged"
        bubble_note = f"""
        <div style='color: gray; font-style: italic; font-size: 13px; margin-top: 5px;'>
            *This message was flagged for hate speech and was not sent.*
        </div>
        """
    else:
        # AI classifier check
        result = classifier(user_input)[0]
        label = result['label'].lower()
        score = result['score']

        if label in ["toxic", "hate", "offensive"] and score >= 0.85:
            bubble_class += " flagged"
            bubble_note = f"""
            <div style='color: gray; font-style: italic; font-size: 13px; margin-top: 5px;'>
                *This message was flagged by AI (confidence: {score:.2f}) and was not sent.*
            </div>
            """

    # Final message
    message_html = f"""
    <div class="chat-container">
        <div class="{bubble_class}">
        <div class="name-label">You:</div>
        {safe_input}
        <div>{bubble_note}</div>
        </div>
    </div>
"""


    # Save to session history
    st.session_state.messages.append(message_html)
    st.rerun()
