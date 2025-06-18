from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
@app.route('/')
def home():
    return "✅ Middleware is running and ready to receive Monnit data."
def webhook():
    data = request.get_json()
    
    target_sensor_id = '1275050'
    results = []

    for sensor in data.get('sensorMessages', []):
        sensor_id = sensor.get('sensorID')

        if sensor_id == target_sensor_id:
            value = sensor.get('plotValues')
            timestamp = sensor.get('messageDate')

            cleaned_data = {
                "deviceId": sensor_id,
                "data": {
                    "distance_cm": value
                },
                "timestamp": timestamp
            }

            results.append(cleaned_data)
            print(cleaned_data)  # Later: publish to Fogwing here

    return jsonify({"status": "success", "processed": len(results)}), 200