"""
pip install supabase
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

os.chdir(Path(__file__).parent)

def get_client():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    return create_client(url, key)


def add_note(supabase: Client, content: str):
    # 1. Insert into table "notes" - column "content
    res = supabase.table("notes").insert({"content": content}).execute()

    if not res.data:
        return RuntimeError(f"Insert failed: {res}")

    return res.data[0]

def list_notes(supabase: Client, limit: int = 10):
    # Read the rows
    res = (
        supabase.table("notes")
        .select("id", "content", "created_at")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return res.data or []

def main():
    # 1. Get a client
    supabase = get_client()

    # # 2. Write note
    # note = add_note(supabase, "Hallo Mohamed")
    # print("Inserted:", note)

    # 3. Read notes
    notes = list_notes(supabase)
    print("Last notes:")
    for note in notes:
        print(f"- {note["content"]} - {note["created_at"]}")

if __name__ == "__main__":
    main()