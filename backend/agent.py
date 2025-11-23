import uuid

from backend.storage import load_processed, get_prompts, save_draft
from backend.llm_client import run_llm


def email_chat(email_id, query):
    processed = load_processed()
    email = processed[email_id]

    prompt = f"""
You are an assistant that helps users understand emails.

Email content:
Subject: {email.get('subject', '')}
Body: {email.get('content', '')}

User request:
{query}

If the user asks for tasks, you may summarize the action items implied by the email.
Respond concisely and clearly.
"""
    response = run_llm(prompt)
    return response


def draft_reply(email_id, tone="Formal"):
    """
    Draft a reply to an existing email.
    Uses:
    - auto-reply prompt
    - email thread context (subject + body)
    - tone selection
    Stores draft for later review.
    """
    processed = load_processed()
    prompts = get_prompts()
    email = processed[email_id]

    auto_reply_instruction = prompts.get("reply", "Draft a polite reply based on the email context.")

    final_prompt = f"""
You are an email reply drafting assistant.

Use this auto-reply instruction:
{auto_reply_instruction}

You are replying in this email thread:
Original Subject: {email.get('subject', '')}
Original Body: {email.get('content', '')}

Tone: {tone}

Return ONLY valid JSON in this exact format:
{{
  "subject": "Re: <short subject line>",
  "body": "full reply email body here",
  "follow_ups": ["optional follow-up 1", "optional follow-up 2"],
  "metadata": {{
     "category": "{email.get('category', '')}",
     "action_items": {{"tasks": []}}
  }}
}}
Do not include any explanation outside the JSON.
"""

    draft_json = run_llm(final_prompt)

    # Save draft for later review
    draft_id = f"reply_{email_id}"
    save_draft(draft_id, draft_json)

    return draft_json


def generate_new_draft(user_instruction):
    """
    Generate a brand new email (not a reply).
    Stores the draft for later review.
    """
    prompt = f"""
You are an assistant that writes new emails from scratch.

User request:
{user_instruction}

Return ONLY valid JSON in this exact format:
{{
  "subject": "<short subject line>",
  "body": "full email body here",
  "follow_ups": ["optional follow-up 1", "optional follow-up 2],
  "metadata": {{
     "category": "General",
     "action_items": {{"tasks": []}}
  }}
}}
Do not include any explanation outside the JSON.
"""

    draft_json = run_llm(prompt)

    # unique ID for new draft
    draft_id = f"new_{uuid.uuid4().hex[:8]}"
    save_draft(draft_id, draft_json)

    return draft_json

