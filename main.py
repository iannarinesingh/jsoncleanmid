from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import json
import time

app = Flask(__name__)

# === MQTT Config ===
MQTT_BROKER = "iothub.fogwing.net"
MQTT_PORT = 8883
MQTT_USERNAME = "7a6e91607a6954d2"
MQTT_PASSWORD = "Upvevwcf2&"
MQTT_TOPIC = "fwent/edge/7a6e91607a6954d2/inbound"
CLIENT_ID = "1151-2077-2785-5193"

# === MQTT Client Setup ===
mqtt_client = mqtt.Client(client_id=CLIENT_ID)
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.tls_set()

def on_connect(client, userdata, flags, rc):
    print("🟢 Connected with result code", rc)
    if rc == 0:
        print("✅ MQTT Connection successful")
    else:
        print("❌ MQTT Connection failed — Code:", rc)

def on_disconnect(client, userdata, rc):
    print("🔌 MQTT Disconnected — Code:", rc)

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect

mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()  # Run MQTT loop in background

@app.route('/')
def home():
    return "✅ Middleware is running and ready to receive Monnit data."

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("📥 Received data:", data)

    target_sensor_id = '1275050'
    results = []

    for sensor in data.get('sensorMessages', []):
        sensor_id = sensor.get('sensorID')
        print("🔎 Checking sensor ID:", sensor_id)

        if sensor_id == target_sensor_id:
            print("🎯 MATCHED Sensor ID")

            value = sensor.get('plotValues')
            timestamp = sensor.get('messageDate')

            # Construct payload for Fogwing
            cleaned_data = {
                "deviceId": sensor_id,
                "timestamp": timestamp.replace(" ", "T") + "Z",
                "data": {
                    "distance_cm": value
                }
            }

            # Send to Fogwing
            payload = json.dumps(cleaned_data)
            result = mqtt_client.publish(MQTT_TOPIC, payload)
            print("📤 Sent to Fogwing:", payload)
            print("📤 MQTT Publish Result Code:", result.rc)

            results.append(cleaned_data)

    return jsonify({"status": "success", "processed": len(results)}), 200