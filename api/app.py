from flask import Flask, jsonify, request, render_template
import os
import socket

from db import (
    device_exists,
    get_devices,
    get_measurements,
    get_latest_measurement,
    get_measurements_for_device,
    insert_measurement,
)
from validation import validate_measurement
from cache import get_latest_from_cache, set_latest_in_cache

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "v1")
POD_NAME = socket.gethostname()


@app.get("/")
def dashboard():
    return render_template("index.html", version=APP_VERSION, pod=POD_NAME)


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "version": APP_VERSION,
        "pod": POD_NAME,
    }), 200


@app.get("/devices")
def devices():
    return jsonify(get_devices()), 200


@app.get("/measurements")
def measurements():
    return jsonify(get_measurements()), 200


@app.get("/devices/<device_id>/latest")
def latest(device_id):

    # om sensorn finns
    if device_exists(device_id):
        # försök hämta den senaste mätningen från Redis
        cached_measurement = get_latest_from_cache(device_id)
        # om mätningen finns i Redis, returnera den
        if cached_measurement is not None:
            return jsonify(cached_measurement), 200
        # om mätningen inte finns i Redis, hämta den från PostgreSQL
        latest_measurement = get_latest_measurement(device_id)

        if latest_measurement is not None:
            # spara mätningen i Redis så att den kan hittas snabbare nästa gång
            set_latest_in_cache(device_id, latest_measurement)

            return jsonify(latest_measurement), 200
        else: 
            return jsonify({"error": "no measurement found"}), 404
    else:
        return jsonify({"error": "deviceId not found"}), 404


@app.get("/devices/<device_id>/measurements")
def device_history(device_id):
    if device_exists(device_id):
        device_measurements = get_measurements_for_device(device_id)
        return jsonify(device_measurements), 200
    else:
        return jsonify({"error": "deviceId not found"}), 404       


@app.post("/measurements")
def create_measurement():
    data = request.get_json(silent=True) or {}
    errors = validate_measurement(data)

    if errors:
        print(f"INVALID measurement from {data.get('deviceId', 'unknown')}: {errors}")
        return jsonify({"errors": errors}), 400
    
    if device_exists(data["deviceId"]):
        saved_measurement = insert_measurement(data)
        # uppdatera Redis med den nya senaste mätningen
        set_latest_in_cache(data["deviceId"], saved_measurement)

        print(f"Measurement saved: {data}")

        return jsonify({"measurement": saved_measurement}), 201
    else:
        return jsonify({"error": "deviceId not found"}), 400


@app.get("/statistics")
def statistics():
    # Utmaning:
    # Returnera antal devices, antal measurements, avg temp etc.
    return jsonify({"message": "Optional challenge"}), 501


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
