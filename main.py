from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import json
from datetime import datetime

app = Flask(__name__)

# === MQTT Configuration ===
MQTT_BROKER = "iothub.fogwing.net"
MQTT_PORT = 8883
MQTT_USERNAME = "7a6e91607a6954d2"
MQTT_PASSWORD = "Upvevwcf2&"
MQTT_TOPIC = "fwent/edge/7a6e91607a6954d2/inbound"
CLIENT_ID = "1151-2077-2785-5193"

mqtt_connected = False  # Global connection flag

# === MQTT Setup ===
mqtt_client = mqtt.Client(client_id=CLIENT_ID)
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.tls_set()

# === MQTT Callbacks ===
def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    if rc == 0:
        mqtt_connected = True
        print("✅ Connected to MQTT Broker")
    else:
        print("❌ Failed to connect — Code:", rc)

def on_disconnect(client, userdata, rc):
    global mqtt_connected
    mqtt_connected = False
    print("🔌 MQTT Disconnected — Code:", rc)
    if rc != 0:
        print("⚠️ Unexpected disconnect. Trying to reconnect...")
        try:
            client.reconnect()
        except Exception as e:
            print("❌ Reconnect failed:", str(e))

# Attach callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect

# Connect and start background loop
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()

# === Flask Routes ===
@app.route('/')
def home():
    return "✅ Middleware running and listening for Monnit data."

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("📥 Received data:", data)

    results = []
    target_sensor_id = '1275050'

    for sensor in data.get('sensorMessages', []):
        sensor_id = sensor.get('sensorID')
        print("🔎 Checking sensor ID:", sensor_id)

        if sensor_id == target_sensor_id:
            print("🎯 MATCHED Sensor ID")

            try:
                value = sensor.get('plotValues')  # e.g., "29"
                timestamp = sensor.get('messageDate')  # e.g., "2025-06-19 15:02:37"
                timestamp_iso = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").isoformat() + "Z"

                payload = {
                    "deviceId": target_sensor_id,
                    "timestamp": timestamp_iso,
                    "data": {
                        "distance_cm": value
                    }
                }

                if mqtt_connected:
                    result = mqtt_client.publish(MQTT_TOPIC, json.dumps(payload))
                    print("📤 Sent to Fogwing:", json.dumps(payload))
                    print("📤 MQTT Publish Result Code:", result.rc)
                else:
                    print("❌ MQTT not connected. Could not send data.")

                results.append(payload)

            except Exception as e:
                print("❌ Error processing message:", str(e))

    return jsonify({"status": "success", "processed": len(results)}), 200