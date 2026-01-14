"""
> pip install streamlit
> streamlit run app.py
> streamlit run app.py --server.port 8000
"""
import streamlit as st
import requests
import pandas as pd

import os
from pathlib import Path
os.chdir(Path(__file__).parent)

def main():
    st.title("Welcome to my iris species prediction application")

    st.subheader("Choose datasource")
    radio_select = st.radio(
        "Choose dataset to pick from",
        ["Index", "User Defined Parameters"],
        captions=[
            "Choose Index from Test Dataset",
            "Set your own Parameters",
        ],
    )

    url_predict = f"http://127.0.0.1:8000/predict"

    if radio_select == "Index":
        # Add input field
        idx = int(st.text_input("Iris Index", 0))

        # Add Table with test data
        url = f"http://127.0.0.1:8000/get_dataset?select=test"
        response = requests.get(url)
        data = response.json()

        table = pd.DataFrame.from_dict(data=data["data"], orient="index", columns=data["meta"])
        # table.drop(["species"], axis=1, inplace=True)
        st.table(table)

        url_predict = f"http://127.0.0.1:8000/predict?idx={idx}"

    elif radio_select == "User Defined Parameters":
        # Get list of features to create correct number of input fields
        url = f"http://127.0.0.1:8000/list_features"
        response = requests.get(url)
        feature_list = response.json()

        cols = st.columns(len(feature_list))
        params = []

        # Arrange input fields horizontal
        for c, col in enumerate(cols):
            with col:
                params.append(float(st.text_input(feature_list[c].capitalize(), 10).replace(",",".")))
        url_predict = f"http://127.0.0.1:8000/predict?params={params}"

    # 3. Add a Button to predict
    if st.button("Predict"):
        # Get prediction from FastAPI endpoint
        response = requests.get(url_predict)
        data = response.json()
        # Decode json message
        predicted = data["predicted"]
        expected = data["expected"]

        # Get name of species for given numerical index
        url = f"http://127.0.0.1:8000/name_species?index={predicted}"
        response = requests.get(url)
        predicted_name = response.text.replace("\"", "")

        # Show the predicted species in a message
        st.success(f"The predicted species is {predicted_name.capitalize()} (Species Index {predicted})")


if __name__ == "__main__":
    main()