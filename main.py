from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import json
import ssl

app = Flask(__name__)

# === MQTT Configuration ===
MQTT_BROKER = "iothub.fogwing.net"
MQTT_PORT = 8883
MQTT_USERNAME = "7a6e91607a6954d2"
MQTT_PASSWORD = "Upvevwcf2&"
MQTT_TOPIC = "fwent/edge/7a6e91607a6954d2/inbound"
CLIENT_ID = "1151-2077-2785-5193"

connected = False

# === MQTT Setup ===
mqtt_client = mqtt.Client(client_id=CLIENT_ID)
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Set TLS with relaxed verification (for testing)
mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)
mqtt_client.tls_insecure_set(True)

# === MQTT Callbacks ===
def on_connect(client, userdata, flags, rc):
    global connected
    print("🟢 Connected with result code", rc)
    if rc == 0:
        connected = True
        print("✅ Connection successful")

        # Send test message to Fogwing
        test_payload = {
            "deviceId": "1275050",
            "timestamp": "2025-06-19T14:00:00Z",
            "data": {
                "distance_cm": "42"
            }
        }
        result = client.publish(MQTT_TOPIC, json.dumps(test_payload))
        print("📤 TEST Publish Result Code:", result.rc)
    else:
        print("❌ MQTT Connection failed — Code:", rc)

def on_disconnect(client, userdata, rc):
    global connected
    connected = False
    print("🔌 Disconnected from MQTT — Code:", rc)

def on_log(client, userdata, level, buf):
    print("🔍 MQTT Log:", buf)

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_log = on_log

# Start MQTT connection
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
            print("🎯 MATCHED Sensor ID")

            value = sensor.get('plotValues')
            timestamp = sensor.get('messageDate')

            cleaned_data = {
                "deviceId": sensor_id,
                "timestamp": timestamp.replace(" ", "T") + "Z",
                "data": {
                    "distance_cm": value
                }
            }

            if connected:
                mqtt_client.publish(MQTT_TOPIC, json.dumps(cleaned_data))
                print("✅ Sent to Fogwing:", json.dumps(cleaned_data))
                results.append(cleaned_data)
            else:
                print("⚠️ MQTT not connected. Data not sent.")

    return jsonify({"status": "success", "processed": len(results)}), 200