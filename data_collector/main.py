import json
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time
import os

# --- Config InfluxDB ---
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG", "myfactory")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "sensors")
INFLUX_URL = os.getenv("INFLUX_URL", "http://influxdb:8086")

# --- Config MQTT ---
MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "factory/line1/data")

if not INFLUX_TOKEN:
    raise ValueError("❌ INFLUX_TOKEN is not set. Please set the environment variable.")


# initialize InfluxDB client
db_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = db_client.write_api(write_options=SYNCHRONOUS)

def save_to_influx(data):
    try:
        point = Point("machine_status") \
            .tag("machine_id", data["machine_id"]) \
            .field("temperature", float(data["temperature"])) \
            .field("vibration", float(data["vibration"])) \
            .field("status", data["status"])

        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        print(f"✅ Saved to influx: {data['temperature']}°C")
        
    except Exception as e:
        print(f"❌ Error to save to influx: {e}")

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode("utf-8")
        
        data = json.loads(payload_str)
        
        save_to_influx(data)
        
    except Exception as e:
        print(f"Error: {e}")

def run_collector():

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    client.on_connect = lambda c, u, f, rc, props: print("Data collector connected to MQTT")
    client.on_message = on_message

    while True:
        try:
            print(f"Connecting to MQTT {MQTT_BROKER}...")
            client.connect(MQTT_BROKER, 1883, 60)
            break # Jak się uda, wyjdź z pętli while
        except Exception as e:
            print(f" broker not available ({e}). waiting 5s...")
            time.sleep(5)

    client.subscribe(MQTT_TOPIC)
    print("Listening...")
    client.loop_forever()


if __name__ == "__main__":
    run_collector()