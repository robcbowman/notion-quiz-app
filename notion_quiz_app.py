import random
from notion_client import Client

import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env file into environment

# --- CONFIG ---
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
VOCAB_DB_ID = "1cd47d4a-5265-8118-be6b-efde1c229339"
QUIZ_DB_ID = "21f47d4a52658007a98ec1c087f28f8f"

notion = Client(auth=NOTION_TOKEN)

def get_plain_text(prop):
    if not prop:
        return ""
    if "title" in prop and prop["title"]:
        return prop["title"][0]["plain_text"]
    if "rich_text" in prop and prop["rich_text"]:
        return prop["rich_text"][0]["plain_text"]
    if "select" in prop and prop["select"]:
        return prop["select"]["name"]
    if "number" in prop and prop["number"] is not None:
        return str(prop["number"])
    return ""

def clear_quiz_db():
    print("🧹 Deleting existing quiz entries...")
    existing_pages = []
    start_cursor = None
    while True:
        query = notion.databases.query(database_id=QUIZ_DB_ID, start_cursor=start_cursor)
        existing_pages.extend(query["results"])
        if not query.get("has_more"):
            break
        start_cursor = query["next_cursor"]

    for page in existing_pages:
        notion.pages.update(page_id=page["id"], archived=True)

    print(f"✅ Deleted {len(existing_pages)} old quiz items.\n")

def create_quiz_pages(sample_vocab):
    print(f"📝 Creating {len(sample_vocab)} new quiz items...")
    for item in sample_vocab:
        props = item["properties"]

        english = get_plain_text(props.get("English"))
        correct_answer = get_plain_text(props.get("Answer"))
        # User answer (Spanish) starts blank for the quiz
        # Relation property "Ref" links back to vocab item by ID
        vocab_page_id = item["id"]

        new_page_props = {
            "English": {
                "title": [{"text": {"content": english}}]
            },
            "Spanish": {
                "rich_text": []  # blank, user fills this in
            },
            "Answer": {
                "rich_text": [{"text": {"content": correct_answer}}]
            },
            "Reveal": {
                "checkbox": False
            },
            "Result": {
                "select": {"name": "Not answered"}  # or your default option
            },
            "Ref": {
                "relation": [{"id": vocab_page_id}]
            }
        }

        notion.pages.create(
            parent={"database_id": QUIZ_DB_ID},
            properties=new_page_props
        )
    print("✅ Quiz generation complete!")

def main():
    clear_quiz_db()

    # Get all vocab items
    response = notion.databases.query(database_id=VOCAB_DB_ID)
    results = response["results"]

    # Shuffle and take 10 sample for quiz
    random.shuffle(results)
    sample = results[:10]

    create_quiz_pages(sample)

if __name__ == "__main__":
    main()

