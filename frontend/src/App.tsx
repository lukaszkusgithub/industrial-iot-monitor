import { useState, useEffect } from "react";
import axios from "axios";
import {
	LineChart,
	Line,
	XAxis,
	YAxis,
	CartesianGrid,
	Tooltip,
	ResponsiveContainer,
} from "recharts";
import "./App.css";

// Type definitions
interface MachineData {
	machine_id: string;
	temperature: number;
	vibration: number;
	status: string;
	timestamp: string;
}

// Data point for the chart
interface ChartPoint {
	time: string;
	temp: number;
}

function App() {
	const [currentData, setCurrentData] = useState<MachineData | null>(null);
	const [history, setHistory] = useState<ChartPoint[]>([]); // Array for chart data
	const [error, setError] = useState<string>("");

	const fetchMachineData = async () => {
		try {
			const response = await axios.get<MachineData>(
				"http://localhost:8000/api/v1/measurements/LINE_001"
			);
			const newData = response.data;

			setCurrentData(newData);
			setError("");

			// Update Chart History
			setHistory((prevHistory) => {
				const newPoint = {
					time: new Date(newData.timestamp).toLocaleTimeString(),
					temp: newData.temperature,
				};
				// Keep only last 20 points to avoid memory leaks
				const newHistory = [...prevHistory, newPoint];
				if (newHistory.length > 20) newHistory.shift();
				return newHistory;
			});
		} catch (err) {
			console.error(err);
			setError("API Connection Error. Is Docker running?");
		}
	};

	const handleControl = async (command: "START" | "STOP") => {
		try {
			await axios.post("http://localhost:8000/api/v1/control", {
				command,
			});
		} catch (err) {
			console.error(err);
			alert("Failed to send command!");
		}
	};

	useEffect(() => {
		void Promise.resolve().then(() => fetchMachineData());

		const interval = setInterval(() => {
			fetchMachineData();
		}, 1000);

		return () => clearInterval(interval);
	}, []);

	return (
		<div className="dashboard-container">
			<h1>🏭 Smart Factory Monitor</h1>

			{error && <div className="error-box">{error}</div>}

			{currentData ? (
				<div className="content-wrapper">
					{/* LEFT SIDE: Metrics & Controls */}
					<div className="machine-card">
						<div className="card-header">
							<h2>{currentData.machine_id}</h2>
							<span
								className={`status-badge ${
									currentData.status === "RUNNING"
										? "green"
										: "red"
								}`}>
								{currentData.status}
							</span>
						</div>

						<div className="metrics-grid">
							<div className="metric-box">
								<h3>Temperature</h3>
								<p
									className="value"
									style={{
										color:
											currentData.temperature > 55
												? "#ff4444"
												: "#00ff88",
									}}>
									{currentData.temperature.toFixed(1)}°C
								</p>
							</div>

							<div className="metric-box">
								<h3>Vibration</h3>
								<p className="value">
									{currentData.vibration.toFixed(2)} mm/s
								</p>
							</div>
						</div>

						<div className="control-panel">
							<button
								onClick={() => handleControl("START")}
								className="btn-start">
								START
							</button>
							<button
								onClick={() => handleControl("STOP")}
								className="btn-stop">
								STOP
							</button>
						</div>
					</div>

					{/* RIGHT SIDE: Real-time Chart */}
					<div className="chart-card">
						<h3>Temperature Trend</h3>
						<div style={{ width: "100%", height: 300 }}>
							<ResponsiveContainer>
								<LineChart data={history}>
									<CartesianGrid
										strokeDasharray="3 3"
										stroke="#333"
									/>
									<XAxis
										dataKey="time"
										stroke="#888"
										style={{ fontSize: "0.8rem" }}
									/>
									<YAxis domain={[0, 80]} stroke="#888" />
									<Tooltip
										contentStyle={{
											backgroundColor: "#16213e",
											border: "1px solid #0f3460",
										}}
										itemStyle={{ color: "#fff" }}
									/>
									<Line
										type="monotone"
										dataKey="temp"
										stroke="#00ff88"
										strokeWidth={3}
										dot={false}
										isAnimationActive={false}
									/>
								</LineChart>
							</ResponsiveContainer>
						</div>
					</div>
				</div>
			) : (
				<p>Loading Machine Data...</p>
			)}
		</div>
	);
}

export default App;
