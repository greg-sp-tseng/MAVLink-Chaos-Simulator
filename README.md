# 🛸 MAVLink Chaos Simulator: RF Environment Testing Sandbox

A robust Python-based simulation framework designed to test MAVLink protocol resilience under harsh RF (Radio Frequency) conditions. This project demonstrates the implementation of "Chaos Engineering" in drone communications, allowing engineers to validate Ground Control Station (GCS) parser logic against packet loss, interference, and complete signal masking.

## 🎯 Core Objectives
* **Validate "Vehicle Mindset"**: Shift from traditional Ask-Response (Polling) to Active Streaming telemetry.
* **Chaos Injection**: Simulate real-world RF instability (70% packet drop rate) and Electronic Warfare (EW) signal jamming.
* **Timeout & Failsafe Detection**: Implement asynchronous GCS monitoring to accurately trigger "Connection Lost" alerts.

## 🏗️ Architecture
The system consists of two decoupled nodes communicating via local UDP (Port 14550):
1.  **`drone_sim.py` (The Vehicle)**: A state-machine-driven broadcaster sending `HEARTBEAT` (#0) and `ATTITUDE` (#30) packets.
2.  **`gcs_parser.py` (The Ground Station)**: A non-blocking receiver equipped with a 3-second heartbeat timeout detector.

## 🚀 Features & Operating Modes
The Drone Simulator features real-time mode switching via terminal keystrokes:
* `[1] Normal Mode`: Continuous, stable telemetry streaming (Ideal conditions).
* `[2] Interference Mode`: Injects a 70% packet drop rate to simulate a degraded RF link.
* `[3] Masking Mode`: Completely halts transmission, simulating hardware failure, crashes, or severe RF jamming.

## 💻 Quick Start
1. Configure a virtual environment and install dependencies:
   ```bash
   pip install pymavlink
2. Launch the GCS Parser in Terminal A:
   python gcs_parser.py
3. Launch the Drone Simulator in Terminal B:
   python drone_sim.py
   ```bash
