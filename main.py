import ssl
import json
import time
import threading
from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt

# --- MQTT Config ---
MQTT_BROKER = "mqtt.fogwing.net"
MQTT_PORT = 8883
MQTT_USERNAME = "your-fogwing-username"  # Replace with your Fogwing username
MQTT_PASSWORD = "your-fogwing-password"  # Replace with your Fogwing password
CLIENT_ID = "1151-2077-2785-5193"         # Replace with the exact Client ID from Fogwing
MQTT_TOPIC = "fwent/edge/data/inbound"    # Or the exact topic assigned in Fogwing

# --- Flask App ---
app = Flask(__name__)

# --- Global State ---
mqtt_connected = False
mqtt_client = mqtt.Client(client_id=CLIENT_ID, clean_session=True)

# --- MQTT Callback Handlers ---

def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    print(f"🟢 Connected with result code {rc}")
    if rc == 0:
        mqtt_connected = True
        print("✅ MQTT Connection successful")
    else:
        print(f"❌ MQTT Connection failed — Code: {rc}")

def on_disconnect(client, userdata, rc):
    global mqtt_connected
    mqtt_connected = False
    print(f"🔌 MQTT Disconnected — Code: {rc}")
    if rc == 7:
        print("⚠️ Authentication failed — check CLIENT_ID, username or password")
    elif rc != 0:
        print("⚠️ Unexpected disconnect. Trying to reconnect...")
        try_reconnect()

def on_log(client, userdata, level, buf):
    print(f"🔍 MQTT Log: {buf}")

# --- MQTT Setup ---

def setup_mqtt():
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)  # Note: Only for testing; use CERT_REQUIRED in production
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_log = on_log
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

def try_reconnect():
    while not mqtt_connected:
        try:
            mqtt_client.reconnect()
            time.sleep(2)
        except Exception as e:
            print(f"🔁 Reconnection error: {e}")
            time.sleep(5)

# --- Flask Routes ---

@app.route("/", methods=["GET"])
def home():
    return "✅ Fogwing MQTT App is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print(f"📥 Received data: {data}")

        if not data:
            return jsonify({"status": "No JSON data received"}), 400

        for sensor in data.get("sensorMessages", []):
            sensor_id = sensor.get("sensorID")
            print(f"🔎 Checking sensor ID: {sensor_id}")

            if sensor_id == "1275050":
                print("🎯 MATCHED Sensor ID")

                mqtt_payload = {
                    "deviceId": str(sensor_id),
                    "timestamp": sensor.get("messageDate"),
                    "data": {
                        "distance_cm": sensor.get("plotValues")
                    }
                }

                payload_str = json.dumps(mqtt_payload)
                print(f"📤 Prepared payload: {payload_str}")

                if mqtt_connected:
                    mqtt_client.publish(MQTT_TOPIC, payload_str, qos=1)
                    print("✅ Published to MQTT")
                else:
                    print("❌ MQTT not connected. Could not send data.")

        return jsonify({"status": "Processed"}), 200

    except Exception as e:
        print(f"❗ Error in webhook: {e}")
        return jsonify({"status": "Error", "message": str(e)}), 500

# --- Main ---
if __name__ == "__main__":
    print("🚀 Starting MQTT client...")
    setup_mqtt()
    print("🌐 Starting Flask server...")
    app.run(host="0.0.0.0", port=10000)