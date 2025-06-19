import paho.mqtt.client as mqtt
import ssl
import time

BROKER = "iothub.fogwing.net"
PORT = 8883

USERNAME = "7a6e91607a6954d2"
PASSWORD = "Upvevwcf2&"
CLIENT_ID = "1151-2077-2785-5193"  # Must be exact from Fogwing portal

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to Fogwing MQTT broker.")
    elif rc == 5:
        print("❌ Not authorized (rc=5). Check credentials or device status.")
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_disconnect(client, userdata, rc):
    print(f"🔌 Disconnected from Fogwing. Code: {rc}")

client = mqtt.Client(client_id=CLIENT_ID, clean_session=False, protocol=mqtt.MQTTv311)
client.username_pw_set(USERNAME, PASSWORD)

client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
client.tls_insecure_set(False)

client.on_connect = on_connect
client.on_disconnect = on_disconnect

print("🔄 Attempting to connect...")

client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    print("🔚 Stopping MQTT client.")
    client.loop_stop()
    client.disconnect()