import os
from pathlib import Path
os.chdir(Path(__file__).parent)

import joblib
from sklearn.pipeline import Pipeline
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def train_model():
    iris = load_iris()
    X = iris.data  # (features)
    y = iris.target  # (species)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    pipe = Pipeline([
        ("scaler", StandardScaler()), # Not necessary for Random Forest
        ("rf", RandomForestClassifier(
            n_estimators=10,
            max_depth=2,
            random_state=42
        ))
    ])

    pipe.fit(X_train, y_train)

    with open("../backend/rf_classifier_v1.joblib", mode="wb") as file:
        joblib.dump(pipe, file)

    y_pred = pipe.predict(X_test)

    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

def load_model():
    with open("../backend/rf_classifier_v1.joblib", mode = "rb") as file:
        model = joblib.load(file)
    return model

if __name__ == "__main__":
    train_model()