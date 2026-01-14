from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import pickle

import os
from pathlib import Path
os.chdir(Path(__file__).parent)

def load_iris_data(select:str= "all"):
    os.chdir(Path(__file__).parent)
    # Load iris data
    # from local folder if available otherwise download from sklearn
    try:
        with open("./iris_data.pkl", mode = "rb") as file:
            iris = pickle.load(file)
        print("Loaded Iris data locally")
    except FileNotFoundError:
        iris = load_iris()
        print("Loaded Iris data from server")

        with open("./iris_data.pkl", mode="wb") as file:
            pickle.dump(iris, file)
    except Exception as e:
        print(e)

    feature_names = iris.feature_names
    target_names = iris.target_names.tolist()
    X = iris.data  # (features)
    y = iris.target  # (species)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    if select == "all":
        return X, y
    elif select == "test":
        return X_test, y_test
    elif select == "train":
        return X_train, y_train
    elif select == "attributes":
        return feature_names, target_names
    else:
        return None