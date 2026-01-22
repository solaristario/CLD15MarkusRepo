"""
pip install "fastapi[standard]"
fastapi dev app.py
"""
import os
import time
import requests
import logging.config
import joblib

from pathlib import Path
from fastapi import FastAPI
from dotenv import load_dotenv
from datetime import datetime, UTC
from textblob import TextBlob
from supabase import create_client, Client

os.chdir(Path(__file__).parent)

# Load logging configuration file
logging.config.fileConfig('../config/logging_config.ini')

# Get personal OpenWeatherMap API Key
load_dotenv("../.env")
OWM_API_KEY  = os.environ.get("OWM_API_KEY")

SUPA_URL = os.environ.get("SUPABASE_URL")
SUPA_API_KEY = os.environ.get("SUPABASE_API_KEY")
SUPA_DB_PWD  = os.environ.get("SUPABASE_DB_PWD")

LANG = "de"

# 1. Create the APP
app = FastAPI()

@app.get("/weather_coords")
def weather_coords(lon:float=None, lat:float=None, session:str=None):
    if not (lon and lat):
        logging.error("No coordinates provided (lon, lat)")
        return {}

    try:
        lon = float(lon)
        lat = float(lat)
    except Exception as e:
        logging.error(f"Exception converting coordinates to float {e}")
        return {}
    else:
        weather_data = {}
        # Get weather data from OWM with weather endpoint
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric&lang={LANG}"

        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            tstp = datetime.fromtimestamp(int(data['dt']),
                                          tz=UTC).astimezone()  # Convert unix timestamp to localized datetime timestamp
            tstp_str = tstp.replace(microsecond=0).isoformat()
            name = data["name"]
            temp = data["main"]["temp"]
            descp_id = data["weather"][0]["id"]
            descp = data["weather"][0]["description"]

            # Save weather data
            weather_data = {
                "city": name,
                "date": tstp_str,
                "temperature": temp,
                "weather_id": descp_id,
                "description": descp
            }
            # logging.info(f"Sucessfully got weather data for city {name}\n{weather_data}")

            data_db = {
                "session": session,
                "weath_city": name,
                # "weath_date": name,
                "weath_lon": lon,
                "weath_lat": lat,
                "weath_temp": temp,
                "weath_descp": descp,
                "weath_id": descp_id
            }
            try:
                data_to_cloud(session=session, data=data_db)
            except Exception as e:
                logging.error(f"Failed to send weather data to database {e}")

            return weather_data

        else:
            logging.error(f"Weather API Request Failed with Status Code {response.status_code}")

@app.get("/weather_city")
def weather_city(city:str = None, session:str=None):
    """
    asd
    """
    if city is None:
        logging.error(f"No city name provided")
        return {}

    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=3&appid={OWM_API_KEY}"
    logging.info(f"Requesting {url}")
    response = requests.get(url)

    if response.status_code == 200:
        try:
            data = response.json()
            lon = float(data[0]["lon"])
            lat = float(data[0]["lat"])
            name = data[0]["name"]
        except Exception as e:
            logging.error(f"Exception getting coordinates for {city} {e}")
            return {}
        else:
            logging.info(f"Got coordinates for {city} as {name}: Longitude: {lon}, Latitude: {lat}")
            return weather_coords(lon=lon, lat=lat, session=session)

@app.get("/sentiment")
def sentiment(text:str = None, session:str=None):
    blob = TextBlob(text)
    logging.debug(f"Text blobs: {blob.tags}")
    print(blob.tags)

    mean_score = 0

    for sentence in blob.sentences:
        logging.debug(f"{sentence} ----> {sentence.sentiment.polarity}")
        mean_score += sentence.sentiment.polarity

    data_db = {
        "session": session,
        "comment_text": text,
        "comment_score": mean_score
    }

    try:
        data_to_cloud(session=session, data=data_db)
    except Exception as e:
        logging.error(f"Failed to send sentiment data to database {e}")

    return mean_score

def weather_to_sqlite(session:str=None):
    """
    SQLite
    """
    pass

def data_to_cloud(session:str=None, data:dict=None):
    """
    Supabase DB
    """
    db_cols = {
        "session": str,
        "weath_city": str,
        # "weath_date": str,
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

    if len(data_db) == 0:
        logging.error(f"No valid data provided for {session}, {data}")
        return []
    else:
        supabase = create_client(SUPA_URL, SUPA_API_KEY)

        def list_session(supabase: Client):
            tries = 0
            while tries <= 3:
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
