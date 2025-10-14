import streamlit as st
import re
import html

# Page setup
st.set_page_config(page_title="NESTAR Messaging Filter", layout="centered")
st.title("NESTAR Hate Crime Messaging Detection System")
st.caption("Microsoft Teams Simulation")

# Chat UI styling
st.markdown("""
<style>
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 20px;
}
.chat-bubble {
    padding: 10px 15px;
    border-radius: 15px;
    max-width: 75%;
    word-wrap: break-word;
    font-size: 16px;
}
.incoming {
    background-color: #f1f1f1;
    align-self: flex-start;
}
.outgoing {
    background-color: #e1f5fe;
    align-self: flex-end;
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
</style>
""", unsafe_allow_html=True)

# Pattern-based keywords
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

# State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display prior messages
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
st.markdown("""
<div class="chat-bubble incoming">
    <div class="name-label">Alex:</div>
    Hi, how are you going?
</div>
""", unsafe_allow_html=True)

for bubble in st.session_state.chat_history:
    st.markdown(bubble, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Input form
with st.form(key="chat_form"):
    user_input = st.text_input("You:", value="", key="user_input")
    submitted = st.form_submit_button("Send")

    if submitted and user_input.strip():
        label, score, matched_keywords = keyword_detector(user_input)
        safe_input = html.escape(user_input)

        bubble_class = "chat-bubble outgoing"
        bubble_note = ""

        if label == "toxic (keyword)":
            bubble_class += " flagged"
            bubble_note = "<div style='color: gray; font-style: italic; font-size: 13px; margin-top: 5px;'>*This message was flagged and not sent.*</div>"

        message_html = f"""
        <div class="{bubble_class}">
            <div class="name-label">You:</div>
            {safe_input}
            {bubble_note}
        </div>
        """

        st.session_state.chat_history.append(message_html)
        st.rerun()
