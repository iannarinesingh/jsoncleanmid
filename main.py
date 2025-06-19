from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import ssl
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

connected = False

# === MQTT Callbacks ===
def on_connect(client, userdata, flags, rc):
    global connected
    print("🟢 MQTT connected with result code:", rc)
    if rc == 0:
        connected = True
        print("✅ Connection successful")
    else:
        print("❌ Connection failed — Code:", rc)

def on_disconnect(client, userdata, rc):
    global connected
    connected = False
    print("🔌 Disconnected with result code:", rc)

def on_log(client, userdata, level, buf):
    print("🔍 MQTT Log:", buf)

# === MQTT Client Setup ===
mqtt_client = mqtt.Client(client_id=CLIENT_ID, clean_session=False)
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_log = on_log

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
mqtt_client.loop_start()

# === Flask Routes ===
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
            print("🎯 MATCHED SENSOR:", sensor_id)

            value = sensor.get('plotValues')
            timestamp = sensor.get('messageDate')

            # Convert timestamp to ISO8601
            iso_timestamp = timestamp.replace(" ", "T") + "Z"

            cleaned_data = {
                "deviceId": sensor_id,
                "timestamp": iso_timestamp,
                "data": {
                    "distance_cm": value
                }
            }

            if connected:
                payload = json.dumps(cleaned_data)
                result = mqtt_client.publish(MQTT_TOPIC, payload, qos=1)
                print("📤 Published to Fogwing:", payload)
                print("📦 Publish result:", result.rc)
            else:
                print("⚠️ MQTT not connected — skipping publish")

            results.append(cleaned_data)

    return jsonify({"status": "success", "processed": len(results)}), 200