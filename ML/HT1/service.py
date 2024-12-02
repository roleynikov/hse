from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import pandas as pd
import pickle
import numpy as np
import json


app = FastAPI()

with open("ridge.pkl", 'rb') as f:
    ridge = pickle.load(f)

class Item(BaseModel):
    name: str
    year: int
    km_driven: int
    fuel: str
    seller_type: str
    transmission: str
    owner: str
    mileage: str
    engine: str
    max_power: str
    torque: str
    seats: float


def predict(dataf):
    dataf['mileage']=dataf['mileage'].apply(lambda x: np.nan if pd.isna(x) else float(x.split()[0]))
    dataf['engine']=dataf['engine'].apply(lambda x: np.nan if pd.isna(x) else float(x.split()[0]))
    dataf.drop('torque',axis=1,inplace=True)
    dataf.drop('name',axis=1,inplace=True)
    dataf['max_power']=dataf['max_power'].apply(lambda x: np.nan if pd.isna(x) or x == ' bhp' else float(x.split()[0]))
    return ridge.predict(dataf)

@app.get("/")
def root():
    return {"Hello!"}

    
@app.post("/predict_item")
def predict_item(item: Item) -> float:
    df = pd.DataFrame([json.loads(item.model_dump_json())])
    return predict(df)


@app.post("/predict_items")
def upload(file: UploadFile = File(...)) -> FileResponse:
    df = pd.read_csv(file.file)
    df['selling_price'] = predict(df)
    file.file.close()
    df.to_csv('result.csv')
    return FileResponse(path = 'result.csv')

