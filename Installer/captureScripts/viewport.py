from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample data for demonstration purposes
snapshots_logs = [
    {"timeIndex": 1, "message": "Snapshot log 1"},
    {"timeIndex": 2, "message": "Snapshot log 2"},
    # Add more snapshot logs here
]

sensor_logs = [
    {"sensorType": "A", "message": "Sensor log A1"},
    {"sensorType": "B", "message": "Sensor log B1"},
    {"sensorType": "A", "message": "Sensor log A2"},
    # Add more sensor logs here
]

@app.route('/AutoCapture', methods=['GET'])
def auto_capture():
    try:
        data = request.get_json()
        status = data.get("status")
        service_type = data.get("serviceType")

        # Implement your logic for AutoCapture here
        # For demonstration, just returning the received data
        response = {"status": status, "serviceType": service_type}
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/ViewSnapshotsLogs', methods=['GET'])
def view_snapshots_logs():
    try:
        data = request.get_json()
        time_index_start = data.get("timeIndexStart")
        time_index_stop = data.get("timeIndexStop")

        # Implement your logic for ViewSnapshotsLogs here
        # For demonstration, returning sample snapshot logs
        response = [log for log in snapshots_logs if time_index_start <= log["timeIndex"] <= time_index_stop]
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/ViewSensorLogs', methods=['GET'])
def view_sensor_logs():
    try:
        data = request.get_json()
        sensor_type = data.get("sensorType")

        # Implement your logic for ViewSensorLogs here
        # For demonstration, returning sample sensor logs
        response = [log for log in sensor_logs if log["sensorType"] == sensor_type]
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
