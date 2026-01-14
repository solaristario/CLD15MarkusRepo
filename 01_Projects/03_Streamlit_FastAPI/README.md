# README
App zur Bestimmung der Art einer Schwertlilie (Iris) basierend auf den geometrischen Merkmalen.  
Datensatz von sklearn.datasets -> load_iris
### 2 Möglichkeiten zur Dateneingabe
- Auswahl einer Probe aus den Testdaten
- Eingabe eigener Proben-Parameter

## File Structure
~~~
03_Streamlit_FastAPI
│ 
├── frontend/ 
│   └── app.py                  # Streamlit application 
│ 
├── backend/ 
│   ├── app.py                  # FastAPI app 
│   ├── load_iris_data.py       # Module to load and save iris dataset from sklearn
│   ├── rf_classifier_v1.joblib # Trained ML model 
│   ├── iris_data.pkl           # Locally saved data from sklearn iris dataset
│ 
├── training/ 
│   └── train_model.py          # Model training script 
│ 
├── requirements.txt 
└── README.md
~~~

## Frontend
Streamlit
~~~
pip install streamlit
streamlit run app.py --server.port 8000
~~~

## Backend
FastAPI
~~~
pip install "fastapi[standard]"
fastapi dev app.py
~~~

~~~
Base URL: http://backendip/  
Authentication: No, open access
~~~

### Endpoints

| Method | Path                  | Description                 | Auth |
|--------|-----------------------|-----------------------------|------|
| GET    | /predict?idx=&params= | Predict species with ML     | ❌   |
| GET    | /get_dataset?select=  | Get dataset                 | ❌   |
| GET    | /name_species?index=  | Get name for species number | ❌   |
| GET    | /list_features        | List all feature names      | ❌   |


   