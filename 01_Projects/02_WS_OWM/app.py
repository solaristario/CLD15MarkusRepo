import os
from pathlib import Path
os.chdir(Path(__file__).parent)

import logging.config
import requests
from pprint import pprint
from datetime import datetime, UTC, timezone
from dotenv import load_dotenv
import sqlite3

# Load of logging configuration file
logging.config.fileConfig('./cfg/logging_config.ini')

# Create logger
logger = logging.getLogger(__name__)

load_dotenv(".env")
API_KEY =  os.environ.get("API_KEY")

def fetch_owm_weather_data(city):
    # logging.info(f"Get coordinates for city {city} from OWM direct endpoint")
    # Get coordinates for city name from OWM direct endpoint
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=3&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        try:
            lon = data[0]["lon"]
            lat = data[0]["lat"]
            logging.info(f"Sucessfully got coordinates for city {city}, latitude {lat}°, longitude {lon}°")
        except Exception as e:
            logging.info(f"Exception getting coordinates {e}")
            return {}
        else:
            if lon and lat:
                weather_data = {} # Collecting weather data
                weather_codes = {} # Collecting weather description for multiple languages
                weather_codes = weather_codes_from_db() # Fill with existing descriptions from db

                weather_id = 9999
                for l, lang in enumerate(["en", "de"]):
                    if len(weather_data)==0 or (weather_id in weather_codes and (lang not in weather_codes[weather_id] or not weather_codes[weather_id][lang])):
                        if (weather_id in weather_codes and (lang not in weather_codes[weather_id] or not weather_codes[weather_id][lang])):
                            logging.info(f"Requesting weather data for missing weather description for {weather_id} in {lang}")
                        # logging.info(f"Get weather data for city {city} from OWM with weather endpoint")
                        # Get weather data from OWM with weather endpoint
                        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang={lang}"
                        response = requests.get(url)
                        data = response.json()

                        if response.status_code == 200:
                            tstp = datetime.fromtimestamp(int(data['dt']), tz=UTC).astimezone() # Convert unix timestamp to localized datetime timestamp
                            name = data["name"]
                            temp = data["main"]["temp"]
                            weather_id   = data["weather"][0]["id"]
                            descp_lang = data["weather"][0]["description"]

                            # Save weather description for language
                            if weather_id not in weather_codes:
                                weather_codes[weather_id] = {lang: descp_lang}
                                logging.info(f"New weather id {weather_id}: {weather_codes[weather_id]}")
                            else:
                                weather_codes[weather_id][lang] = descp_lang
                                if lang not in weather_codes[weather_id]:
                                    logging.info(f"New weather description in {lang} for {weather_id}: {weather_codes[weather_id]}")

                            # Save weather data
                            if len(weather_data)==0:
                                weather_data = {
                                    "city_query": city,
                                    "city": name,
                                    "date": tstp,
                                    "temperature": temp,
                                    "weather_id": weather_id
                                }
                            logging.info(f"Sucessfully got weather data for city {city} ({name})\n{weather_data}")

                weather_data_to_db(weather_data)

                weather_codes_to_db(weather_codes)


    else:
        logging.info(f"Error requesting coordinates with status code {response.status_code}")
        return {}



def create_weather_db():
    conn = sqlite3.connect('./db/weather.db')
    c = conn.cursor()

    sql = """CREATE TABLE IF NOT EXISTS weather_data
             (
                 ID integer primary key,
                 city_query text,
                 city text,
                 date_unix integer,
                 date_str text,
                 temp real,
                 weather_id integer
             )"""
    c.execute(sql)
    conn.commit()

    sql = """CREATE TABLE IF NOT EXISTS weather_codes
             (
                 ID integer primary key,
                 weather_id integer,
                 descp_en text,
                 descp_de text
             )"""
    c.execute(sql)
    conn.commit()

    conn.close()

def weather_data_to_db(weather_data):
    conn = sqlite3.connect('./db/weather.db')
    c = conn.cursor()

    city_query = weather_data["city_query"]
    city = weather_data["city"]
    date = weather_data["date"]
    date_unix = date.replace(microsecond=0).timestamp()
    date_str = date.replace(microsecond=0).isoformat()
    temperature = weather_data["temperature"]
    weather_id = weather_data["weather_id"]

    params = (city_query, city, date_unix, date_str, temperature, weather_id)

    sql = """INSERT INTO weather_data (city_query, city, date_unix, date_str, temp, weather_id) \
             VALUES (?, ?, ?, ?, ?, ?)"""
    c.execute(sql, params)
    conn.commit()

    conn.close()

def weather_codes_to_db(weather_codes):
    conn = sqlite3.connect('./db/weather.db')
    c = conn.cursor()

    for weather_id in weather_codes:
        sql = """SELECT * FROM weather_codes WHERE weather_id = ?"""
        result = c.execute(sql, (weather_id,)).fetchall()

        if len(result)==0:
            params = (weather_id,)
            sql = """INSERT INTO weather_codes (weather_id) VALUES (?)"""
            c.execute(sql, params)
            conn.commit()

        for lang in weather_codes[weather_id]:
            descp_col = f"descp_{lang}"
            descp = weather_codes[weather_id][lang]
            params = (descp, weather_id)
            sql = f"""UPDATE weather_codes SET {descp_col} = ? WHERE weather_id = ?"""
            c.execute(sql, params)
            conn.commit()

    conn.close()

def weather_codes_from_db():
    weather_codes = {}
    conn = sqlite3.connect('./db/weather.db')
    c = conn.cursor()

    params = ()
    sql = """SELECT * FROM weather_codes"""
    cursor = c.execute(sql, params)
    cols = [description[0] for description in cursor.description]
    result = cursor.fetchall()
    for vals in result:
        weather_id = vals[cols.index("weather_id")]
        weather_codes[weather_id] = {}

        for col, val in zip(cols, vals):
            if col.startswith("descp_"):
                lang = col.replace("descp_", "")
                weather_codes[weather_id][lang] = val

    return weather_codes

def get_weather_for_cities():
    for city in ["Berlin", "Aachen", "Stuttgart"]:
        fetch_owm_weather_data(city)

def main():
    create_weather_db()
    get_weather_for_cities()


if __name__ == "__main__":
    main()