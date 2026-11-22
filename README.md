# Project 31 – Dockerise Your API

A scikit-learn classification model (Iris) served through a **FastAPI** REST API and packaged as a **Docker** image, so it can be built once and run the same way on any machine.

## Project structure

```
dockerise-api/
├── app/main.py            FastAPI app (/, /health, /predict)
├── model/model.joblib     trained pipeline (created by train.py)
├── tests/test_api.py      pytest tests (3 tests)
├── train.py               trains and saves the model
├── requirements.txt       runtime dependencies (pinned versions)
├── requirements-dev.txt   runtime + pytest + httpx
├── Dockerfile             image definition
├── .dockerignore          files excluded from the image
└── docker-compose.yml     one-command build and run
```

## API endpoints

| Method | Path       | Description                                  |
|--------|------------|----------------------------------------------|
| GET    | `/`        | Welcome message                              |
| GET    | `/health`  | Health check (also reports if model is loaded) |
| POST   | `/predict` | Returns predicted class and probabilities    |

Example request body for `/predict`:

```json
{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}
```

Input is validated with Pydantic (values must be between 0 and 15), so invalid input returns a `422` error.

## How to run

### 1. Run locally (without Docker)

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python train.py
python -m pytest -q
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs

> Train the model inside this virtual environment so it uses the same scikit-learn version as `requirements.txt`.

### 2. Build the Docker image

```bat
docker build -t iris-api:1.0 .
docker images
```

### 3. Run the container

```bat
docker run -d --name iris-api -p 8000:8000 iris-api:1.0
docker ps
docker logs iris-api
```

### 4. Test it

Open http://localhost:8000/docs, or:

```bat
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d "{\"sepal_length\":5.1,\"sepal_width\":3.5,\"petal_length\":1.4,\"petal_width\":0.2}"
```

### 5. Stop and remove

```bat
docker stop iris-api
docker rm iris-api
```

### Docker Compose (optional)

```bat
docker compose up --build -d
docker compose down
```

## Key Docker concepts used in this project

### Image vs. container

An **image** is a read-only template that contains the operating system layer, Python, the installed libraries, my code and the trained model. A **container** is a running instance of an image. I can start many containers from one image, and deleting a container does not delete the image. In this project, `docker build` creates the image `iris-api:1.0`, and `docker run` starts a container named `iris-api` from it.

### Why `requirements.txt` is copied first (layer caching)

Every instruction in a Dockerfile creates a cached layer. Docker reuses a layer only if that instruction and everything before it are unchanged. Installing the libraries is the slowest step (about 70 seconds in my build), and `requirements.txt` rarely changes, while my code changes often. So the Dockerfile copies `requirements.txt` and runs `pip install` first, and copies the application code afterwards. When only the code changes, Docker reuses the cached install layer and the rebuild takes seconds instead of minutes.

### Why the server binds to `0.0.0.0`

Inside a container, `127.0.0.1` (localhost) means only the container itself. If uvicorn listened only on localhost, requests coming through the published port (`-p 8000:8000`) from my computer would never reach it. Binding to `0.0.0.0` makes uvicorn listen on all of the container's network interfaces, so traffic forwarded by Docker reaches the API.

### Why a non-root user

By default, processes in a container run as `root`. If the application were ever compromised, an attacker would have root rights inside the container. The Dockerfile creates a normal user (`appuser`) and switches to it with `USER appuser`, following the principle of least privilege. The API only needs to read its own files, so it does not need root.

### Why a healthcheck

A container can be "running" while the application inside it has crashed or failed to load the model. The `HEALTHCHECK` instruction makes Docker call the `/health` endpoint every 30 seconds and mark the container as `healthy` or `unhealthy`. This is visible in `docker ps`, and orchestration tools can use it to restart or replace unhealthy containers. In my run, `docker ps` showed `Up ... (healthy)`.

## Results (screenshots)

**1. Unit tests pass**
![Tests passed](Screenshots/01-pytest-passed.png)

**2. Docker image build**
![Docker build](Screenshots/02-docker-build.png)

**3. Image created**
![Docker images](Screenshots/03-docker-images.png)

**4. Container running and healthy**
![Docker ps](Screenshots/04-docker-ps-healthy.png)

**5. Prediction from the running container**
![Predict result](Screenshots/05-docs-predict-setosa.png)


## Troubleshooting

- **`No module named 'app'` when running `pytest`:** run `python -m pytest -q` instead, so the project folder is on Python's path.
- **Port 8000 already in use:** run with `-p 8080:8000` and open http://localhost:8080.
- **Model/scikit-learn version warning:** retrain with `python train.py` inside the virtual environment, then rebuild the image.
- **Docker command not found or daemon not running:** start Docker Desktop and wait for "Engine running".
