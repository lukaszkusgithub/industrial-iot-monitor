# Smart Factory IIoT Monitor

![Project Status](https://img.shields.io/badge/status-active-success)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=flat&logo=react&logoColor=%2361DAFB)
![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)
![InfluxDB](https://img.shields.io/badge/InfluxDB-22ADF6?style=flat&logo=InfluxDB&logoColor=white)

## 📖 Overview

**Smart Factory IIoT Monitor** is a full-stack Industrial IoT application designed to simulate, monitor, and control industrial machinery in real-time.

The system uses a microservices architecture to collect telemetry data (Temperature, Vibration) via **MQTT**, store it in a Time-Series Database (**InfluxDB**), and visualize it on a **React** dashboard. Key features include **full-duplex communication**, allowing operators to remotely START/STOP the machine from the web interface.

## 🚀 Key Features

* **Real-time Monitoring:** Live visualization of sensor data (Temperature, Vibration) via WebSockets/Polling.
* **Remote Control (SCADA):** Bidirectional communication allowing the user to stop the machine via the Dashboard.
* **Time-Series Analysis:** Historical data tracking using InfluxDB and Recharts.
* **Microservices:** Fully containerized environment using Docker & Docker Compose.
* **Simulation:** Python-based machine simulator generating realistic physics-based data.

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | React, TypeScript, Vite | Interactive Dashboard with Charts |
| **Backend API** | Python, FastAPI | REST API & MQTT Bridge |
| **Database** | InfluxDB v2 | High-performance Time-Series Database |
| **Message Broker** | Eclipse Mosquitto | MQTT Transport Layer |
| **Edge/IoT** | Python (Paho-MQTT) | Data Collector & Machine Simulator |
| **DevOps** | Docker, Docker Compose | Containerization & Orchestration |

## 🏗️ System Architecture

Data flows through the system in two directions:

1.  **Monitoring (Read):**
    `Simulator` -> (MQTT) -> `Mosquitto` -> (MQTT) -> `Collector` -> `InfluxDB` -> `FastAPI` -> `React Dashboard`

2.  **Control (Write):**
    `React Dashboard` -> (HTTP POST) -> `FastAPI` -> (MQTT) -> `Mosquitto` -> `Simulator`

## 📂 Project Structure

```bash
SmartFactory/
├── backend_api/       # FastAPI Service (The Receptionist)
├── data_collector/    # Service saving MQTT data to InfluxDB (The Warehouseman)
├── machine_simulator/ # Python script simulating sensor data (The Machine)
├── frontend/          # React + TypeScript Dashboard
├── mosquitto/         # MQTT Broker config
├── docker-compose.yml # Orchestration of all services
└── .env               # Environment variables (Git ignored)
```


## ⚡ Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js & npm (for local frontend development)
  
### 1. Clone the repository
```bash
git clone https://github.com/lukaszkusgithub/industrial-iot-monitor.git

cd industrial-iot-monitor
```

### 2. Configure Environment Variables

Create a ``.env`` file in the root directory. You can use the example below:

```ini
# --- INFLUXDB CONFIG ---
INFLUX_TOKEN=my-super-secret-admin-token
INFLUX_ORG=myfactory
INFLUX_BUCKET=sensors
INFLUX_URL=http://influxdb:8086

# --- MQTT CONFIG ---
MQTT_BROKER=mosquitto
MQTT_PORT=1883
MQTT_TOPIC=factory/line1/data
```

### 3. Build and Run Backend Services

Use Docker Compose to spin up the Simulator, Broker, Database, Collector, and API.

```bash
docker-compose up --build
```

Wait until you see logs indicating "Connected to MQTT" and "Uvicorn running".

### 4. Run Frontend (Dashboard)

Open a new terminal window to run the React application:
```bash
cd frontend
npm install
npm run dev
```

Open your browser at `http://localhost:5173`.

## 🎮 Usage

1. **Monitor**: Watch the Temperature and Vibration gauges update every second.

2. **Analyze**: Observe the real-time chart drawing the temperature trend (last 20 points).

3. **Control**:
   - Click **STOP**: The Simulator will receive the command via MQTT, change status to ``STOPPED``, and temperature will drop.

   - Click **START**: The machine resumes operation and values return to normal range.

## 🧠 Learning Outcomes

This project demonstrates proficiency in:

- Designing **Event-Driven Architectures** using MQTT.

- Handling **Time-Series Data** with InfluxDB and Flux query language.

- Building **RESTful APIs** with Python/FastAPI.

- Implementing **Containerization** best practices with Docker.

- Creating modern frontends with **React Hooks**, **TypeScript** and **Recharts**.

## 📄 License
Distributed under the MIT License.
