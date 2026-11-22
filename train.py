"""Train a small scikit-learn pipeline and save it for the API.

Swap this for your own saved pipeline from Project 30 if you like -
just keep the same dict layout: {"pipeline": ..., "target_names": [...]}.
"""
from pathlib import Path

import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42, stratify=iris.target
)

pipeline = Pipeline(
    [("scale", StandardScaler()), ("clf", LogisticRegression(max_iter=500))]
)
pipeline.fit(X_train, y_train)
print(f"Test accuracy: {pipeline.score(X_test, y_test):.3f}")

out = Path("model")
out.mkdir(exist_ok=True)
joblib.dump(
    {"pipeline": pipeline, "target_names": list(iris.target_names)},
    out / "model.joblib",
)
print("Saved model/model.joblib")
