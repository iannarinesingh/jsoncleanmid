import paho.mqtt.client as mqtt
import time

# ==== Fogwing MQTT Credentials ====
BROKER = "iothub.fogwing.net"
PORT = 8883
USERNAME = "7a6e91607a6954d2"          # Replace with your actual UID from Fogwing
PASSWORD = "Upvevwcf2&"        # Replace with your device token from Fogwing
CLIENT_ID = "1151-2077-2785-5193"   # Replace with your registered Client ID

# Track connection status
connected = False

# ==== Callback: On Connect ====
def on_connect(client, userdata, flags, rc):
    global connected
    print(f"🟢 Connected with result code: {rc}")
    if rc == 0:
        connected = True
        print("✅ Connection established with Fogwing.")
    else:
        print("❌ Connection failed. Check credentials or network.")

# ==== Callback: On Disconnect ====
def on_disconnect(client, userdata, rc):
    global connected
    connected = False
    print(f"🔌 Disconnected from Fogwing. Code: {rc}")

# ==== MQTT Client Setup ====
client = mqtt.Client(client_id=CLIENT_ID)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()  # Uses default system CA certs

client.on_connect = on_connect
client.on_disconnect = on_disconnect

# ==== Connect and Loop Forever ====
print("🔄 Attempting to connect to Fogwing...")
client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

# Wait and confirm connection
for i in range(10):
    if connected:
        break
    print(f"⏳ Waiting for connection... ({i+1}/10)")
    time.sleep(1)

if connected:
    print("🟢 Staying connected. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("👋 Shutting down...")
else:
    print("❌ Could not connect. Exiting...")

client.loop_stop()
client.disconnect()