import paho.mqtt.client as mqtt
import time

BROKER = "iothub.fogwing.net"
PORT = 8883
USERNAME = "7a6e91607a6954d2"
PASSWORD = "Upvevwcf2&"
CLIENT_ID = "1151-2077-2785-5193"  # Must match Fogwing's assigned client ID

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connection established with Fogwing.")
    elif rc == 5:
        print("❌ Connection refused: Not authorized.")
    else:
        print(f"❌ Connection failed with result code: {rc}")

def on_disconnect(client, userdata, rc):
    print(f"🔌 Disconnected from Fogwing. Code: {rc}")

client = mqtt.Client(client_id=CLIENT_ID)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()  # Required if Fogwing uses SSL/TLS

client.on_connect = on_connect
client.on_disconnect = on_disconnect

print("🔄 Attempting to connect to Fogwing...")

client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

# Keep the program running for debugging
try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    print("Stopping...")
    client.loop_stop()
    client.disconnect()