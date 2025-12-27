import os
import time
import json
import random
import sys
import paho.mqtt.client as mqtt

sys.stdout.reconfigure(encoding="utf-8")

# Configuration
BROKER = os.getenv("MQTT_BROKER", "mosquitto")
PORT = 1883
TOPIC_DATA = "factory/line1/data"
TOPIC_CMD = "factory/line1/cmd"

MACHINE_STATUS = "RUNNING"


# Callback: Executed when the client connects to the broker
def on_connect(client, userdata, flags, rc, props):
    if rc == 0:
        print(f"✅ SIMULATOR: Connected to Broker! Return Code: {rc}")
        # SUBSCRIPTION IS KEY - we need to listen for commands immediately
        print(f"✅ SIMULATOR: Subscribing to topic: {TOPIC_CMD}")
        client.subscribe(TOPIC_CMD)
    else:
        print(f"❌ SIMULATOR: Connection failed, return code: {rc}")


# Callback: Executed when a message is received on a subscribed topic
def on_message(client, userdata, msg):
    global MACHINE_STATUS
    try:
        # Decode payload to string
        payload = msg.payload.decode("utf-8").upper()
        print(f"MESSAGE RECEIVED: [{payload}] on topic [{msg.topic}]")

        if "STOP" in payload:
            print("🛑 STOPPING MACHINE...")
            MACHINE_STATUS = "STOPPED"
        elif "START" in payload:
            print("🟢 STARTING MACHINE...")
            MACHINE_STATUS = "RUNNING"

    except Exception as e:
        print(f"❌ Error processing command: {e}")


# Main execution function
def run():
    print("🚀 Starting Simulator v2 (DEBUG MODE)...")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        try:
            print(f"⏳ Connecting to {BROKER}...")
            client.connect(BROKER, PORT, 60)
            break
        except Exception as e:
            print(f"❌ Broker unreachable ({e}). Waiting 5s...")
            time.sleep(5)

    client.loop_start()

    while True:
        if MACHINE_STATUS == "STOPPED":
            temp = 20.0  # Room temperature
            vib = 0.0
        else:
            temp = round(random.uniform(40.0, 60.0), 2)
            vib = round(random.uniform(0.0, 5.0), 2)

        data = {
            "machine_id": "LINE_001",
            "timestamp": time.time(),
            "temperature": temp,
            "vibration": vib,
            "status": MACHINE_STATUS,
        }

        try:
            client.publish(TOPIC_DATA, json.dumps(data))
        except Exception as e:
            print(f"❌ Error publishing data: {e}")

        print(f"STATUS: {MACHINE_STATUS} | Waiting for commands...")
        time.sleep(1)


if __name__ == "__main__":
    run()
