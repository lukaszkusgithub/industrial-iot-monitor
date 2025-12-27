from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from influxdb_client import InfluxDBClient
import os
import paho.mqtt.client as mqtt
from pydantic import BaseModel

# --- CONFIGURATION ---
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG", "myfactory")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "sensors")
INFLUX_URL = os.getenv("INFLUX_URL", "http://influxdb:8086")

MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_CMD_TOPIC = "factory/line1/cmd"

if not INFLUX_TOKEN:
    raise ValueError("❌ INFLUX_TOKEN is not set. Please set the environment variable.")


# --- INITIALIZATION ---
app = FastAPI(
    title="Smart Factory API", description="API for accessing production line data"
)

# CORS Policy (Cross-Origin Resource Sharing)
# This allows our React frontend (running on a different port) to access this API.
# In a real production environment, you should specify exact origins instead of ["*"].
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to InfluxDB
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()

# --- HELPER FUNCTIONS ---


def send_mqtt_command(command: str):
    print(command)
    # try:
    #     client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    #     client.connect(MQTT_BROKER, 1883, 60)
    #     client.publish(MQTT_CMD_TOPIC, command)
    #     client.disconnect()
    # except Exception as e:
    #     print(f"❌ Error sending MQTT command: {e}")
    #     raise HTTPException(status_code=500, detail="MQTT Broker unavailable")

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        print(f"API: Łączenie z brokerem {MQTT_BROKER}...")
        client.connect(MQTT_BROKER, 1883, 60)

        client.loop_start()

        print(f"API: Wysyłanie rozkazu {command} na temat {MQTT_CMD_TOPIC}...")
        msg_info = client.publish(MQTT_CMD_TOPIC, command)

        msg_info.wait_for_publish(timeout=2)

        print("API: Rozkaz wysłany pomyślnie!")

        client.loop_stop()
        client.disconnect()

    except Exception as e:
        print(f"API Błąd MQTT: {e}")
        raise HTTPException(status_code=500, detail=f"MQTT Error: {e}")


# Model danych (co API oczekuje od Reacta)
class CommandRequest(BaseModel):
    command: str


def get_latest_metric(machine_id: str):
    """
    Queries InfluxDB using Flux language to get the last recorded data point.
    """
    # Flux query:
    # 1. Select bucket
    # 2. Filter by time (last 1 minute)
    # 3. Filter by measurement name
    # 4. Filter by machine_id tag
    # 5. Get the last value
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
        |> range(start: -1m)
        |> filter(fn: (r) => r["_measurement"] == "machine_status")
        |> filter(fn: (r) => r["machine_id"] == "{machine_id}")
        |> last()
    '''

    try:
        tables = query_api.query(query)

        # Prepare result dictionary
        result = {
            "machine_id": machine_id,
            "temperature": None,
            "vibration": None,
            "status": "UNKNOWN",
            "timestamp": None,
        }

        # Parse the InfluxDB response tables
        for table in tables:
            for record in table.records:
                field_name = record.get_field()
                field_value = record.get_value()

                if field_name in result:
                    result[field_name] = field_value

                # Capture timestamp from the record
                if result["timestamp"] is None:
                    result["timestamp"] = record.get_time()

        return result

    except Exception as e:
        print(f"Error querying InfluxDB: {e}")
        return None


# --- API ENDPOINTS ---


@app.get("/")
def read_root():
    return {"message": "Smart Factory API is running"}


@app.get("/api/v1/measurements/{machine_id}")
def read_measurement(machine_id: str):
    """
    Get the latest sensor data for a specific machine.
    """
    data = get_latest_metric(machine_id)

    if not data:
        raise HTTPException(
            status_code=404, detail="Machine not found or no recent data"
        )

    return data


if __name__ == "__main__":
    import uvicorn

    # Run the server on localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)


@app.post("/api/v1/control")
def control_machine(req: CommandRequest):
    cmd = req.command.upper()
    if cmd not in ["START", "STOP"]:
        raise HTTPException(
            status_code=400, detail="Invalid command. Use START or STOP"
        )

    send_mqtt_command(cmd)
    return {"status": "success", "message": f"Command {cmd} sent"}
