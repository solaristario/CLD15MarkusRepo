import os

from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

os.chdir(Path(__file__).parent)

load_dotenv()
SUPA_URL = os.environ.get("SUPABASE_URL")
SUPA_API_KEY = os.environ.get("SUPABASE_API_KEY")
SUPA_DB_PWD = os.environ.get("SUPABASE_DB_PWD")

def data_to_cloud(session:str=None, data:dict=None):
    """
    Supabase DB
    """
    db_cols = {
        "session": str,
        "weath_city": str,
        "weath_lon": float,
        "weath_lat": float,
        "weath_temp": float,
        "weath_descp":str,
        "weath_id": int,
        "comment_text": str,
        "comment_score": float
    }
    data_db = {}
    for key, value in data.items():
        if key in db_cols:
            data_db[key] = db_cols[key](value)

    supabase = create_client(SUPA_URL, SUPA_API_KEY)

    def list_session(supabase: Client):
        # Read the rows

        res = (
            supabase
            .table("data_collection")
            .select("*")
            .eq("session", session)
            .execute()
        )

        if res.data:
            res = (
                supabase
                .table("data_collection")
                .update(data_db)
                .eq("session", session)
                .execute()
            )
            return res.data
        else:
            res = (
                supabase
                .table("data_collection")
                .insert(data_db)
                .execute()
            )
            return res.data

    return list_session(supabase)

if __name__ == "__main__":
    session = "ABCD"

    data = {
        "session": session,
        "weath_city": "Göttingen",
        "weath_lon": 99,
        "weath_lat": 11.111,
        "weath_temp": 22.1,
        "weath_descp": "Nebel",
        "weath_id": 500,
        "comment_text": "Hallo Markus",
        "comment_score": 0.5
    }

    notes = data_to_cloud(session=session, data=data)
    print(notes)
