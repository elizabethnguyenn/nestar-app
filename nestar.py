# -----------------------------
# Input Form
# -----------------------------
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

with st.form(key="chat_form"):
    user_input = st.text_input(
        label="",
        value=st.session_state.input_text,
        placeholder="Type a message...",
        key="user_input_box"
    )
    submitted = st.form_submit_button("Send Message")

if submitted and user_input.strip():
    label, score, matched_keywords = keyword_detector(user_input)
    bubble_class = "chat-bubble outgoing"
    bubble_note = ""
    safe_input = html.escape(user_input)

    # Keyword flagged
    if label == "toxic (keyword)":
        bubble_class += " flagged"
        bubble_note = f"""
            <div style='color: gray; font-style: italic; font-size: 13px; margin-top: 5px;'>
                *This message was flagged for hate speech and was not sent.*
            </div>
        """
    else:
        # AI model check
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

    # Construct message HTML
    message_html = f"""
    <div class="chat-container">
        <div class="{bubble_class}">
            <div class="name-label">You:</div>
            {safe_input}
            <div>{bubble_note}</div>
        </div>
    </div>
    """

    # Update message and clear input
    st.session_state.last_message_html = message_html
    st.session_state.user_input_box = ""  # ✅ this clears the input field

    st.rerun()
