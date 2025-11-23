import json
from .llm_client import run_llm
from backend.storage import save_processed, get_prompts

def load_emails():
    with open("mock_inbox/inbox.json", "r") as f:
        return json.load(f)

def process_inbox():
    emails = load_emails()
    prompts = get_prompts()
    processed = {}

    for id, email in emails.items():
        category_prompt = f"{prompts['categorization']}\n\nEmail:\n{email['content']}"
        category = run_llm(category_prompt)

        action_prompt = f"{prompts['action']}\n\nEmail:\n{email['content']}"
        action = run_llm(action_prompt)

        processed[id] = {
            "sender": email["sender"],
            "subject": email["subject"],
            "timestamp": email["timestamp"],
            "content": email["content"],
            "category": category,
            "action_items": action
        }


    save_processed(processed)
    return processed
