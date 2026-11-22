import os
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
from fastapi import FastAPI
from pydantic import BaseModel, Field

MODEL_PATH = Path(os.getenv("MODEL_PATH", "model/model.joblib"))
state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the model once when the container starts, not on every request.
    bundle = joblib.load(MODEL_PATH)
    state["pipeline"] = bundle["pipeline"]
    state["classes"] = bundle["target_names"]
    yield
    state.clear()


app = FastAPI(
    title="Iris Classifier API",
    description="A scikit-learn pipeline served with FastAPI and packaged in Docker.",
    version="1.0.0",
    lifespan=lifespan,
)


class IrisFeatures(BaseModel):
    sepal_length: float = Field(..., gt=0, lt=15, examples=[5.1], description="cm")
    sepal_width: float = Field(..., gt=0, lt=15, examples=[3.5], description="cm")
    petal_length: float = Field(..., gt=0, lt=15, examples=[1.4], description="cm")
    petal_width: float = Field(..., gt=0, lt=15, examples=[0.2], description="cm")


class Prediction(BaseModel):
    prediction: str
    probabilities: dict[str, float]


@app.get("/")
def root():
    return {"message": "Iris API is running. See /docs for the interactive docs."}


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": "pipeline" in state}


@app.post("/predict", response_model=Prediction)
def predict(features: IrisFeatures):
    row = [[
        features.sepal_length,
        features.sepal_width,
        features.petal_length,
        features.petal_width,
    ]]
    pipeline = state["pipeline"]
    probs = pipeline.predict_proba(row)[0]
    classes = state["classes"]
    best = int(probs.argmax())
    return Prediction(
        prediction=classes[best],
        probabilities={c: round(float(p), 4) for c, p in zip(classes, probs)},
    )
