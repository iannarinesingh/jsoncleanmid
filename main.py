import paho.mqtt.client as mqtt
import ssl
import time
import json

def on_connect(client, userdata, flags, rc):
    print("🟢 Connected:", rc)

def on_disconnect(client, userdata, rc):
    print("🔌 Disconnected:", rc)

client = mqtt.Client(client_id="1151-2077-2785-5193")
client.username_pw_set("7a6e91607a6954d2", "Upvevwcf2&")
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)

client.on_connect = on_connect
client.on_disconnect = on_disconnect

client.connect("iothub.fogwing.net", 8883)
client.loop_start()

time.sleep(3)

payload = {
    "deviceId": "1275050",
    "timestamp": "2025-06-19T16:11:00Z",
    "data": {
        "distance_cm": "28"
    }
}

client.publish("fwent/edge/7a6e91607a6954d2/inbound", json.dumps(payload))

time.sleep(3)
client.loop_stop()
client.disconnect()