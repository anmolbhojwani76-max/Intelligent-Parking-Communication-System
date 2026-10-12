# Setup and usage

[Project overview and team](../README.md)

## Run on Windows

Install Python 3.10 or newer, then open the repository folder in VS Code. From the folder containing the batch files, run:

```powershell
.\INSTALL_WINDOWS.bat
.\START_WINDOWS.bat
```

Run the installer once and wait for it to finish successfully before starting the project. Installation requires internet access; the local demo can run offline afterwards.

Open these pages if they do not launch automatically:

- Dashboard: http://127.0.0.1:8090
- Sensor controls: http://127.0.0.1:8091

Keep the terminal open while the project is running. Press **Ctrl+C** to stop it.

You can also start it directly from the repository folder:

```powershell
cd IntelligentParking
python -m pip install -r requirements.txt
python run_demo.py
```

## Automatic simulation

Simulation starts by default. Cars arrive and leave in a repeating 80-second cycle, so no manual slot changes are needed.

Use **Pause transmission** on the sensor page to stop reports. After about eight seconds, the dashboard marks the slots as unknown. Resume transmission to restore updates.

These are simulated readings sent through the same TCP and MQTT components used by camera mode.

## Camera setup

Use a fixed webcam facing eight parking spaces. For a tabletop demo, print `PARKING_BOARD.html` from the repository folder and use toy cars or small objects.

1. Open the sensor page and select **Camera detection**.
2. Click **Enable camera** and allow access.
3. Align the eight zones with the spaces, or draw custom zones in A01–A08 order.
4. Clear all spaces and click **Capture empty reference**.
5. Click **Start detection**, then place or remove an object in a slot.

The detector compares each zone with the empty reference and waits for a sustained change before updating occupancy. Keep the camera steady and the sensor tab visible. Capture a new reference if the camera position or lighting changes.

Camera frames stay in the browser; only occupancy states are sent to the local sensor program.

## Connect two laptops over Wi-Fi

Connect both laptops to the same Wi-Fi network. Run the following commands from the `IntelligentParking` folder.

**Laptop A — server**

Install the requirements, then run:

```powershell
python run_demo.py --lan --no-sensor
```

Use `ipconfig` in another terminal to find laptop A's Wi-Fi IPv4 address.

**Laptop B — sensor**

Copy the project to this laptop and run the command below, replacing the example IP with laptop A's address:

```powershell
python sensor.py --gateway-host 192.168.1.10
```

On laptop B, open `http://127.0.0.1:8091` for camera controls and `http://192.168.1.10:8090` for the central dashboard.

Allow the required connections through the firewall on your trusted private network. Some campus Wi-Fi networks block communication between devices.

Use one sensor program at a time for these eight slots. The TCP sensor connection crosses Wi-Fi; the MQTT broker and central subscriber run on laptop A. Running everything on one laptop uses loopback and does not demonstrate wireless transmission.

## Main files

Paths below are inside `IntelligentParking/`.

| File | Purpose |
|---|---|
| `run_demo.py` | Starts the project components. |
| `sensor.py` | Provides simulation, camera controls and TCP reporting. |
| `gateway.py` | Validates sensor reports and publishes them to MQTT. |
| `broker.py` | Runs the AMQTT broker. |
| `server.py` | Receives MQTT updates and serves the dashboard. |
| `web/vision.js` | Compares camera frames with the empty reference. |
| `test_core.py` | Checks validation and state handling. |

Default ports: TCP gateway **5050**, MQTT **18884**, dashboard **8090**, sensor page **8091**.

Reports use the MQTT topic `parking/v2/snapshot` with QoS 1. Each report contains the source, session, sequence number and eight slot states. The server rejects repeated or older sequence numbers within tracked sessions and expires stale reports.

## Checks and common issues

From the `IntelligentParking` folder, run:

```powershell
python test_core.py
```

Details of the software and browser checks are in [TEST_RESULTS.md](TEST_RESULTS.md). Physical webcam, Windows and two-laptop Wi-Fi testing still needs to be completed on the demonstration equipment.

- **Batch file not recognised in PowerShell:** include `.\` before its name.
- **Missing Python package:** rerun the installer with the Python version used to start the project.
- **Port already in use:** stop the previous project process with Ctrl+C.
- **Camera unavailable:** use the local sensor address on the camera laptop and check browser permission.
- **False occupancy:** keep lighting steady, recapture the empty reference or adjust the threshold.
- **Slots remain unknown:** check transmission, camera calibration and the server IP. Keep the camera tab visible.

## Limitations

Camera mode detects visual changes, not vehicle types. Hands, shadows and other objects can also mark a space as occupied, so it works best with a controlled tabletop setup.

The project provides availability guidance, not reservations. It stores state in memory and is intended for a trusted local network; authentication, encryption and persistent storage are not implemented. A future hardware version could use an ESP32 with IR or ultrasonic sensors.

## References

- [Python sockets](https://docs.python.org/3/library/socket.html)
- [Paho MQTT](https://eclipse.dev/paho/clients/python/docs/)
- [AMQTT](https://amqtt.readthedocs.io/en/latest/references/broker_config/)
- [Browser camera API](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)
