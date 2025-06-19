from fastapi import APIRouter
from pydantic import BaseModel
import joblib
import numpy as np

router = APIRouter(prefix="/api", tags=["Diagnosis"])

# Load model & feature metadata
model = joblib.load("app/model/rf_model.pkl")
feature_names = joblib.load("app/model/model_features.pkl")

# Skema input dari user (frontend)
class InputData(BaseModel):
    nasal_discharge: str
    skin_lesions: str
    sneezing: str
    animal_type: int
    fever: str
    lameness: str
    wool_issue: str
    lethargy: str
    diarrhea: str
    labored_breathing: str
    age: int
    reduced_mobility: str
    dehydration: str
    duration: int
    weight_loss: str
    milk_yield_issue: str

# Fungsi preprocessing input
def preprocess_user_input(user_input: dict, feature_names: list) -> list:
    result = {}
    yesno_map = {"yes": 1, "no": 0, "true": 1, "false": 0}
    for col in feature_names:
        val = user_input.get(col, None)
        if val is None:
            result[col] = 0
        elif isinstance(val, str):
            result[col] = yesno_map.get(val.strip().lower(), 0)
        else:
            result[col] = val
    return [result[col] for col in feature_names]

# Endpoint prediksi
@router.post("/predict")
def predict_disease(data: InputData):
    user_dict = data.dict()
    X = np.array([preprocess_user_input(user_dict, feature_names)])
    pred = model.predict(X)[0]
    return {
        "diagnosa": pred,
        "message": f"Berdasarkan gejala, kemungkinan besar hewan mengalami: {pred}"
    }