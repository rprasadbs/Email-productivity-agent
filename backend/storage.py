import json
import os

PROMPT_FILE = "prompts/default_prompts.json"
PROCESSED_FILE = "data/processed.json"
DRAFT_FILE = "data/drafts.json"


def get_prompts():
    if not os.path.exists(PROMPT_FILE):
        # safe defaults
        return {
            "categorization": "Categorize this email into: Important, Newsletter, Spam, To-Do.",
            "action": "Extract tasks from this email and respond in JSON.",
            "reply": "Draft a polite reply based on the email context."
        }
    with open(PROMPT_FILE, "r") as f:
        return json.load(f)


def save_prompts(cat, act, rep):
    os.makedirs(os.path.dirname(PROMPT_FILE), exist_ok=True)
    with open(PROMPT_FILE, "w") as f:
        json.dump(
            {
                "categorization": cat,
                "action": act,
                "reply": rep
            },
            f,
            indent=4
        )


def save_processed(data):
    os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
    with open(PROCESSED_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_processed():
    if not os.path.exists(PROCESSED_FILE):
        return {}
    with open(PROCESSED_FILE, "r") as f:
        return json.load(f)


# ---------- DRAFT STORAGE ----------

def save_draft(draft_id, draft_content):
    """
    draft_content can be a string or JSON string.
    """
    os.makedirs(os.path.dirname(DRAFT_FILE), exist_ok=True)

    drafts = {}
    if os.path.exists(DRAFT_FILE):
        with open(DRAFT_FILE, "r") as f:
            drafts = json.load(f)

    drafts[draft_id] = draft_content

    with open(DRAFT_FILE, "w") as f:
        json.dump(drafts, f, indent=4)


def load_drafts():
    if not os.path.exists(DRAFT_FILE):
        return {}
    with open(DRAFT_FILE, "r") as f:
        return json.load(f)


def update_draft(draft_id, new_content):
    drafts = load_drafts()
    drafts[draft_id] = new_content
    os.makedirs(os.path.dirname(DRAFT_FILE), exist_ok=True)
    with open(DRAFT_FILE, "w") as f:
        json.dump(drafts, f, indent=4)
