from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import json
import ssl

app = Flask(__name__)

# ========== MQTT CONFIG ==========
MQTT_BROKER = "mqtt.fogwing.net"
MQTT_PORT = 8883
MQTT_USERNAME = "7a6e91607a6954d2"  # your Fogwing device username
MQTT_PASSWORD = "Upvevwcf2&"        # your Fogwing device password
CLIENT_ID = "1151-2077-2785-5193"   # Fogwing Client ID
MQTT_TOPIC = "fwent/edge/7a6e91607a6954d2/inbound"

# ========== MQTT SETUP ==========
mqtt_client = mqtt.Client(client_id=CLIENT_ID)
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

is_connected = False  # Flag for connection state

def on_connect(client, userdata, flags, rc):
    global is_connected
    if rc == 0:
        is_connected = True
        print("✅ MQTT Connection successful")
    else:
        print(f"❌ MQTT Connection failed — Code: {rc}")

def on_disconnect(client, userdata, rc):
    global is_connected
    is_connected = False
    print(f"🔌 MQTT Disconnected — Code: {rc}")

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()

# ========== ROUTES ==========
@app.route('/')
def home():
    return "✅ Middleware is running and ready to receive Monnit data."

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("📥 Received data:", json.dumps(data, indent=2))

    target_sensor_id = '1275050'
    results = []

    for sensor in data.get('sensorMessages', []):
        sensor_id = sensor.get('sensorID')
        print("🔎 Checking sensor ID:", sensor_id)

        if sensor_id == target_sensor_id:
            print("🎯 MATCHED Sensor ID")
            value = sensor.get('plotValues')
            timestamp = sensor.get('messageDate')

            # Prepare Fogwing payload
            payload = {
                "deviceId": target_sensor_id,
                "timestamp": timestamp,
                "data": {
                    "distance_cm": value
                }
            }
            json_payload = json.dumps(payload)
            print("📤 Prepared payload:", json_payload)

            if is_connected:
                result = mqtt_client.publish(MQTT_TOPIC, json_payload)
                print("📡 Sent to Fogwing, result:", result.rc)
            else:
                print("❌ MQTT not connected. Could not send data.")

            results.append(payload)

    return jsonify({"status": "success", "processed": len(results)}), 200