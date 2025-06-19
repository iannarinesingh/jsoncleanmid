from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import json
import ssl
import threading
import time

app = Flask(__name__)

# ========== MQTT CONFIG ==========
MQTT_BROKER = "iothub.fogwing.net"
MQTT_PORT = 8883
MQTT_USERNAME = "7a6e91607a6954d2"
MQTT_PASSWORD = "Upvevwcf2&"
CLIENT_ID = "1151-2077-2785-5193"
MQTT_TOPIC = "fwent/edge/7a6e91607a6954d2/inbound"

# ========== MQTT CLIENT SETUP ==========
mqtt_client = mqtt.Client(client_id=CLIENT_ID)
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

is_connected = False

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

def start_mqtt():
    while True:
        try:
            print("🔄 Attempting MQTT connect...")
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
            mqtt_client.loop_forever()
        except Exception as e:
            print(f"🔥 MQTT connection error: {e}")
            time.sleep(10)

# ========== ROUTES ==========
@app.route('/')
def home():
    return "✅ Flask app is live."

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("📥 Received data:", json.dumps(data, indent=2))

    results = []
    for sensor in data.get('sensorMessages', []):
        sensor_id = sensor.get('sensorID')
        print("🔎 Checking sensor ID:", sensor_id)

        if sensor_id == '1275050':
            print("🎯 MATCHED Sensor ID")
            value = sensor.get('plotValues')
            timestamp = sensor.get('messageDate')

            payload = {
                "deviceId": sensor_id,
                "timestamp": timestamp,
                "data": {
                    "distance_cm": value
                }
            }
            message = json.dumps(payload)
            print("📤 Payload:", message)

            if is_connected:
                mqtt_client.publish(MQTT_TOPIC, message)
                print("📡 Published to MQTT.")
            else:
                print("❌ MQTT not connected.")

            results.append(payload)

    return jsonify({"status": "done", "processed": len(results)})

# ========== START MQTT BACKGROUND THREAD ==========
threading.Thread(target=start_mqtt, daemon=True).start()