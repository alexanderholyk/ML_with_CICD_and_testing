import sys
from pathlib import Path

# Make the project root importable so we can `import main`
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.parametrize("text,true_label", [
    ("I absolutely loved this movie!", "positive"),
    ("This director has amazing vision.", "positive"),
    ("What a wild ride. I can't wait to watch it again.", "positive"),
])
def test_predict_positive(text, true_label):
    response = client.post(
        "/predict",
        json={"text": text, "true_label": true_label}
    )
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data


@pytest.mark.parametrize("text,true_label", [
    ("What a waste of time!", "negative"),
    ("What was the director thinking? Honestly I could make a better movie.", "negative"),
    ("Terrible. A serious contender for worst film of the year.", "negative"),
])
def test_predict_negative(text, true_label):
    response = client.post(
        "/predict",
        json={"text": text, "true_label": true_label}
    )
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data


def test_predict_malformed_data():
    # text missing
    response = client.post(
        "/predict",
        json={"text": "I hate this item!", "malformed_label": "negative"}
    )
    assert response.status_code == 422


def test_predict_missing_text():
    # text missing
    response = client.post(
        "/predict",
        json={"true_label": "positive"}
    )
    assert response.status_code == 422


def test_predict_invalid_true_label():
    # invalid true_label
    response = client.post(
        "/predict",
        json={"text": "Not sure", "true_label": "invalid"}
    )
    assert response.status_code == 422