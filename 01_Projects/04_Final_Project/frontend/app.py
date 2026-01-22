"""

streamlit run app.py --server.port 8000
"""
import os
import uuid
import streamlit as st
import requests
from pathlib import Path
from datetime import datetime

os.chdir(Path(__file__).parent)


def main():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    st.write("Session ID:", st.session_state.session_id)

    api_url = "http://127.0.0.1:8000" # URL to backend API
    st.title("Welcome to my app")

    st.subheader("Weather Forecast")
    city = str(st.text_input("Your City", ""))

    if st.button("Submit", key="btn_cty"):
        if len(city)<=1:
            st.error(f"City Name required")
        else:
            response = requests.get(f"{api_url}/weather_city?city={city}&session={st.session_state.session_id}")
            if not response.status_code == 200:
                st.error(f"Weather API Request Failed with Status Code {response.status_code}")
            else:
                data = response.json()

                city = data["city"]
                tstp_dt = datetime.fromisoformat(data["date"])
                date_str = tstp_dt.strftime("%d.%m.%Y")
                time_str = tstp_dt.strftime("%H:%M")
                descp = data["description"]
                temp = data["temperature"]

                st.success(f"Am {date_str} um {time_str} Uhr lautet das Wetter in {city} {descp} bei {temp}°C")

    comment = str(st.text_input("English Feedback about your Feelings", ""))

    if st.button("Submit", key="btn_comment"):
        response = requests.get(f"{api_url}/sentiment?text={comment}&session={st.session_state.session_id}")
        if not response.status_code == 200:
            st.error(f"Sentiment Analysis API Request Failed with Status Code {response.status_code}")
        else:
            score = float(response.text)
            if score > 0.3:
                st.success(f"Great! Score: {score:.1f}")
            elif score >= 0:
                st.info(f"Okay. Score: {score:.1f}")
            else:
                st.error(f"That's a shame, head up :) Score: {score:.1f}")

if __name__ == "__main__":
    main()