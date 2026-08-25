# källa: https://flask.palletsprojects.com/en/stable/testing/
# hämtar variabeln app/Flask-applikationen

import pytest
from app import app

@pytest.fixture()
def client():
    app.config.update({
        "TESTING": True,
    })
    # simulerar en HTTP-klient
    return app.test_client()


def test_valid_measurement(client):
    # post är en metod som testklienten har: skickar en POST-request till endpointen
    response = client.post("/measurements", json={
            "deviceId": "sensor-001",
            "temperature": 21.5,
            "humidity": 45.0,
            "battery": 90,
        },
    )
    assert response.status_code == 201


def test_invalid_measurement(client):
    response = client.post("/measurements", json={
            "deviceId": "sensor-001",
            "temperature": 21.5,
            "humidity": "ERROR",
            "battery": 90,
        },
    )
    assert response.status_code == 400


def test_get_devices(client):
    response = client.get("/devices")

    assert response.status_code == 200