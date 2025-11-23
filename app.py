import streamlit as st
import datetime

from backend.ingestion import load_emails, process_inbox
from backend.storage import (
    get_prompts,
    save_prompts,
    load_processed,
    load_drafts,
    update_draft,
)
from backend.agent import email_chat, draft_reply, generate_new_draft

st.set_page_config(page_title="Email Productivity Agent")

st.title("📧 Email Productivity Agent")

# Load stored prompts
prompts = get_prompts()

# Sidebar: Prompt Configuration
st.sidebar.header("🧠 Prompt Brain")
categorization = st.sidebar.text_area("Categorization Prompt", prompts.get("categorization", ""))
action_prompt = st.sidebar.text_area("Action Item Prompt", prompts.get("action", ""))
reply_prompt = st.sidebar.text_area("Auto-Reply Prompt", prompts.get("reply", ""))

if st.sidebar.button("Save Prompts"):
    save_prompts(categorization, action_prompt, reply_prompt)
    st.sidebar.success("✅ Prompts Saved")


# Load Inbox
if st.button("Load Inbox"):
    emails = load_emails()
    st.session_state["emails"] = emails
    st.success(f"📥 Loaded {len(emails)} emails!")


# Process Inbox
if st.button("Process Emails"):
    process_inbox()
    st.success("✅ Emails Processed Successfully!")


# Display processed inbox
processed = load_processed()

if processed:

    st.write("### 📌 Select an Email")
    selected = st.selectbox("Emails", list(processed.keys()))

    email = processed.get(selected, {})

    # Email Details
    st.write("### ✉️ Email Details")
    st.write(f"**Sender:** {email.get('sender', 'N/A')}")
    st.write(f"**Subject:** {email.get('subject', 'N/A')}")
    st.write(f"**Timestamp:** {email.get('timestamp', 'N/A')}")
    st.write(f"**Category:** {email.get('category', 'Not Processed')}")

    st.write("---")
    st.write("### 📄 Content")
    st.write(email.get("content", "(No content available)"))

    # Ask questions about email
    query = st.text_input("Ask something about this email:")
    if st.button("Ask"):
        response = email_chat(selected, query)
        st.write("### 🤖 Response")
        st.write(response)

    # Tone selection
    tone = st.selectbox("Select reply tone", ["Formal", "Friendly", "Direct"])

    # Draft reply
    if st.button("Draft Reply"):
        reply = draft_reply(selected, tone)
        st.write("### 📨 Draft Reply (JSON)")
        st.code(reply, language="json")

    # Show urgent emails
    if st.button("Show Urgent Emails"):
        urgent = []

        for id, item in processed.items():

            # safely skip invalid entries
            if not isinstance(item, dict):
                continue

            action_items = item.get("action_items", {})
            if not isinstance(action_items, dict):
                continue

            tasks = action_items.get("tasks", [])

            for task in tasks:
                deadline = task.get("deadline")
                if deadline:
                    try:
                        d = datetime.datetime.strptime(deadline, "%Y-%m-%d")
                        if d <= datetime.datetime.now() + datetime.timedelta(days=2):
                            if id not in urgent:
                                urgent.append(id)
                    except:
                        pass

        st.write("### 🚨 Urgent Emails")
        st.write(urgent if urgent else "✅ No urgent emails found")

else:
    st.info("ℹ️ Load and process emails to begin.")


# --------- DRAFT VIEWER (Phase 3: edit + save drafts) ---------
st.write("---")
st.write("### 📂 Saved Drafts")

drafts = load_drafts()
if drafts:
    draft_ids = list(drafts.keys())
    selected_draft_id = st.selectbox("Select a draft to view/edit", draft_ids)

    current_content = drafts[selected_draft_id]

    edited_content = st.text_area(
        "Draft content (you can edit the JSON or text):",
        value=current_content,
        height=250,
    )

    if st.button("Save Draft Changes"):
        update_draft(selected_draft_id, edited_content)
        st.success("✅ Draft updated!")
else:
    st.write("No drafts saved yet.")


# --------- New email draft generator ---------
st.write("---")
st.write("### 🆕 Generate New Email")

new_text = st.text_input("What do you want to write?")
if st.button("Create Draft"):
    if new_text.strip():
        draft = generate_new_draft(new_text)
        st.write("### ✍️ New Draft (JSON)")
        st.code(draft, language="json")
    else:
        st.warning("Please enter a request to generate a draft.")
