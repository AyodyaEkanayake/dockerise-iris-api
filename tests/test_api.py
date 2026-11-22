from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["model_loaded"] is True


def test_predict_setosa():
    with TestClient(app) as client:
        r = client.post(
            "/predict",
            json={"sepal_length": 5.1, "sepal_width": 3.5,
                  "petal_length": 1.4, "petal_width": 0.2},
        )
        assert r.status_code == 200
        assert r.json()["prediction"] == "setosa"


def test_validation_error():
    with TestClient(app) as client:
        r = client.post("/predict", json={"sepal_length": -1})
        assert r.status_code == 422
