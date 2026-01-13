import os
from pathlib import Path
from fastapi import FastAPI

os.chdir(Path(__file__).parent)

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
