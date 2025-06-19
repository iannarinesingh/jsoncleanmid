from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import json
import uuid
import ssl
import threading
import time

app = Flask(__name__)

# === MQTT CONFIGURATION ===
MQTT_BROKER = "iothub.fogwing.net"
MQTT_PORT = 8883
MQTT_USERNAME = "7a6e91607a6954d2"
MQTT_PASSWORD = "Upvevwcf2&"
MQTT_TOPIC = "fwent/edge/7a6e91607a6954d2/inbound"
CLIENT_ID = f"jsoncleanmid-{uuid.uuid4()}"  # Dynamically generated to avoid Code 7
connected = False

# === MQTT SETUP ===
mqtt_client = mqtt.Client(client_id=CLIENT_ID)
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)  # For testing; adjust for production

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    global connected
    print("🟢 Connected with result code", rc)
    if rc == 0:
        connected = True
        print("✅ MQTT Connection successful")
    else:
        connected = False
        print("❌ MQTT Connection failed — Code:", rc)

def on_disconnect(client, userdata, rc):
    global connected
    connected = False
    print("🔌 MQTT Disconnected — Code:", rc)

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect

# Start MQTT connection in a background thread
def mqtt_loop():
    while True:
        try:
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            mqtt_client.loop_forever()
        except Exception as e:
            print("❗ MQTT Connection error:", e)
            time.sleep(5)

threading.Thread(target=mqtt_loop, daemon=True).start()

# === WEB SERVER ROUTES ===
@app.route('/')
def home():
    return "✅ JSON Cleaner Middleware is running."

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("📥 Received data:", data)

    target_sensor_id = "1275050"
    results = []

    for sensor in data.get('sensorMessages', []):
        sensor_id = sensor.get('sensorID')
        print("🔎 Checking sensor ID:", sensor_id)

        if sensor_id == target_sensor_id:
            print("🎯 MATCHED Sensor ID")

            value = sensor.get('plotValues')
            timestamp = sensor.get('messageDate')

            payload = {
                "deviceId": target_sensor_id,
                "timestamp": timestamp,
                "data": {
                    "distance_cm": value
                }
            }

            if connected:
                mqtt_client.publish(MQTT_TOPIC, json.dumps(payload))
                print("📤 MQTT Published:", json.dumps(payload))
            else:
                print("❌ MQTT not connected. Could not send data.")

            results.append(payload)

    return jsonify({"status": "success", "processed": len(results)}), 200