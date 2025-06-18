from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)

# === MQTT Config ===
MQTT_BROKER = "iothub.fogwing.net"
MQTT_PORT = 8883
MQTT_USERNAME = "7a6e91607a6954d2"
MQTT_PASSWORD = "Upvevwcf2&"
MQTT_TOPIC = "fwent/edge/7a6e91607a6954d2/inbound"
CLIENT_ID = "1151-2077-2785-5193"

# === Connect to MQTT ===
mqtt_client = mqtt.Client(client_id=CLIENT_ID)
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
# Use TLS for secure connection
mqtt_client.tls_set()


def on_connect(client, userdata, flags, rc):
    print("🟢 Connected with result code", rc)
    if rc == 0:
        print("✅ Connection successful")
    else:
        print("❌ Connection failed — Code:", rc)

def on_disconnect(client, userdata, rc):
    print("🔌 Disconnected with result code", rc)

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect

mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()  # 🔄 Starts background thread for MQTT


@app.route('/')
def home():
    return "✅ Middleware is running and ready to receive Monnit data."

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("Received data:",  data)
      
    #This is the sensor ID of the desired MONNIT sensor
    target_sensor_id = '1275050'
    results = []

    for sensor in data.get('sensorMessages', []):
        sensor_id = sensor.get('sensorID')
        print("Checking sensor ID:", sensor.get('sensorID'))
        if sensor_id == target_sensor_id:
            print("MATCHED!")
            value = sensor.get('plotValues')
            timestamp = sensor.get('messageDate')

            cleaned_data = {
                "gatewayMessage": {
                    "distance_cm": value,
                    "timestamp": timestamp
                }
            } 
                
              #cleaned_data = 
              #  "deviceId": sensor_id,
              #  "data": {
              #      "distance_cm": value
              #  },
              #  "timestamp": timestamp
             
 
            
            # send to Fogwing
            mqtt_client.publish(MQTT_TOPIC, json.dumps(cleaned_data))
            print("✅ Published to Fogwing:", json.dumps(cleaned_data))
            
            results.append(cleaned_data)
            #print(cleaned_data)  # Later: publish to Fogwing here

    return jsonify({"status": "success", "processed": len(results)}), 200