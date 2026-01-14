"""
pip install "fastapi[standard]"
fastapi dev app.py
"""
from fastapi import FastAPI
import joblib
import random

from load_iris_data import load_iris_data

import os
from pathlib import Path
os.chdir(Path(__file__).parent)


# 1. Create the APP
app = FastAPI()

# http://127.0.0.1:8000/predict?
@app.get("/predict")
async def predict_iris(idx:int=9999, params:list=None):
    # 1. Load the model
    model = load_model()

    # Option 1: Given idx (index) from test data set
    if params is None:
        # 2. Load iris data for user example selection
        X, y = load_iris_data(select="test")

        # If idx is default choose random number
        if idx == 9999:
            idx = random.randrange(len(X))

        params = X[idx]
        expected = int(y[idx])
        msg = f"Predict iris species from test set (n={len(X)})"

    # Option 2: Given parameter list (params)
    else:
        expected = None
        msg = f"Predict iris species with user parameters"

    # 2. Predict using the model
    predicted = int(model.predict([params])[0])

    # 3. Return the price
    return {
        "msg": msg,
        "index": idx,
        "params": params.tolist(),
        "predicted": predicted,
        "expected": expected
    }


@app.get("/get_dataset")
async def get_dataset(select:str= "all"):
    X, y = load_iris_data(select)
    feature_names, target_names = load_iris_data("attributes")

    result = {
        "meta": feature_names + ["species"],
        "data": {}
    }
    for i, (xi, yi) in enumerate(zip(X, y)):
        data = xi.tolist() + [yi.tolist()]
        result["data"][i] = data

    return result


@app.get("/name_species")
async def name_species(index:int=9999):
    feature_names, target_names = load_iris_data(select="attributes")

    return target_names[index]


@app.get("/list_features")
async def list_features():
    feature_names, target_names = load_iris_data(select="attributes")

    return feature_names


def load_model():
    with open("rf_classifier_v1.joblib", mode ="rb") as file:
        model = joblib.load(file)

    return model