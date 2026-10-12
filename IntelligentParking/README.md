# Intelligent Parking Communication System
## Automatic version using all four CN concepts

The project detects or simulates occupancy automatically and transmits it through this complete path:

**IoT sensor agent → raw TCP socket → gateway → MQTT broker → central subscriber → HTTP dashboard**

Both TCP and MQTT are used in every running demonstration. Wi-Fi is demonstrated by putting the sensor agent and the central services on different laptops connected to the same wireless network.

## Team and advisor

| Team member | Registration number |
|---|---|
| Anmol Bhojwani | RA2411026011395 |
| Vedanth Dama | RA2411026011392 |
| Adyant Behera | RA2411026011384 |
| Mukunthan S | RA2411026011391 |
| Shubham Gajanan Shinde | RA2411026011394 |

Faculty advisor: **Dr. Lakshmi Narayan**, Assistant Professor, Department of Computational Intelligence. SRM Institute of Science and Technology, Kattankulathur.

## What changed from the earlier project

The earlier version required clicking individual spaces to change occupancy. This version has two automatic sources:

- **Camera detection:** a fixed webcam observes eight marked zones. After an empty reference is captured once, frame differences and hysteresis detect sustained occupancy changes. A real camera is required for this mode.
- **Automatic simulation:** a deterministic traffic scenario makes eight vehicles arrive and leave without user input. This demonstrates the real communication pipeline while explicitly identifying the sensor readings as synthetic.

No machine-learning model, paid service, Node.js installation or separate Mosquitto installation is required. The launcher starts a real local AMQTT broker using a Python dependency.

## Windows quick start

Extract the whole ZIP to a new directory. Keep its structure. Do not copy only the Python files.

1. Use Python 3.10 or newer. The package was tested with Python 3.12 on Linux; Windows still needs a check on your laptop.
2. Double-click **INSTALL_WINDOWS.bat** in the outer folder. It installs `amqtt==0.12.1` and `paho-mqtt==2.1.0`. This one-time step needs internet access. Read any installation errors before proceeding.
3. Double-click **START_WINDOWS.bat**. It switches into the correct project folder automatically.
4. Open these addresses if the browser does not launch:
   - Dashboard: http://127.0.0.1:8090
   - Sensor station: http://127.0.0.1:8091
5. Keep the terminal running. Press Ctrl+C there to stop the broker, gateway, subscriber and sensor.

### VS Code alternative

Open the extracted **IntelligentParking** folder in VS Code, then run:

```powershell
python -m pip install -r requirements.txt
python run_demo.py
```

If the terminal is in the outer ZIP extraction folder, first run `cd .\IntelligentParking`. If your Windows installation uses `py`, replace `python` with `py -3` consistently.

After dependencies are installed, the local demonstration does not need internet access. Camera permission is requested by your browser only when you click Enable camera.

## Demonstration 1: automatic traffic, no camera needed

The default sensor mode repeats an 80-second cycle:

| Cycle time | Behaviour |
|---|---|
| 0–5 seconds | All eight slots free |
| 5–40 seconds | One vehicle arrives every five seconds |
| 40–50 seconds | All eight slots occupied |
| 50–71 seconds | Vehicles leave, one every three seconds |
| 71–80 seconds | All slots free before the next cycle |

The dashboard animates occupancy, shows the next confirmed free slot, logs changes and graphs recent observed states. Its mode label says **AUTOMATIC SIMULATION**. Do not present this mode as physical sensing.

Use **Pause transmission** to demonstrate a network/sensor failure. After the final report expires, every slot becomes unknown. Resume to show recovery. There are no manual slot occupancy buttons.

## Demonstration 2: camera-based physical sensing

Open `PARKING_BOARD.html` in the outer folder and print the supplied eight-slot board if useful. Use a fixed webcam aimed down at the parking layout. A USB webcam is convenient; a laptop camera can work if it can see the full board. Arrange eight empty spaces in two rows of four, or define custom rectangles.

1. On the sensor station, choose **Camera detection**.
2. Click **Enable camera** and allow camera access. Use the local address `http://127.0.0.1:8091` on the camera laptop. Plain HTTP on another computer's LAN IP will generally not provide camera permission.
3. Align the board with the eight displayed zones. Alternatively click **Draw custom zones**, then drag eight rectangles in A01–A08 order. Avoid overlapping zones and keep road areas outside the rectangles.
4. Remove every toy car or object and click **Capture empty reference**.
5. Click **Start detection**.
6. Place a toy car or object in one marked area. After a sustained change, the sensor determines occupancy and sends it automatically. The central dashboard updates through TCP and MQTT.
7. Remove the object and let the view return to the empty reference. The slot becomes free again.
8. Adjust the occupancy threshold if necessary. Lower values are more sensitive. After moving the camera or changing lighting significantly, capture a new empty reference.

### Camera behaviour and limits

The algorithm compares sampled RGB pixels with the empty reference, compensates for modest overall brightness change, and estimates the fraction of changed pixels within each rectangle. It requires four consistent processed frames to switch state. The release threshold is lower than the arrival threshold to reduce flicker.

This is **occupancy/obstruction detection**, not vehicle recognition. A hand, bag, shadow or lighting change can trigger occupancy. It is designed for a controlled tabletop demonstration, not outdoor production deployment. It does not estimate vehicle types or registration numbers.

Camera images stay in the browser. The browser posts only eight Boolean states to its local Python sensor agent. Keep the sensor tab visible; browser background throttling or camera loss stops fresh reports. Use side-by-side windows for the sensor and central dashboard. The agent stops forwarding camera readings after 3.5 seconds without fresh camera data; the central state expires up to another 8 seconds after the last forwarded report. Allow about 15 seconds when demonstrating camera stop.

Changing source or zone configuration is setup. Detection thereafter is automatic. If you switch from simulation to camera, the dashboard may briefly show the last **simulation** report until it expires or the first valid camera report arrives; the source label always identifies that report.

## Wi-Fi setup: two laptops

### Laptop A: central services

Install dependencies, connect to a trusted Wi-Fi or phone hotspot, and open the project folder. Run:

```powershell
python run_demo.py --lan --no-sensor
```

Run `ipconfig` in another terminal and note the Wi-Fi IPv4 address, for example `192.168.1.10`. Allow Python on the Windows **private network** if prompted. The gateway uses incoming TCP port **5050** and the dashboard uses **8090**.

### Laptop B: sensor and camera

Copy the **IntelligentParking** folder to laptop B. This sensor-only process uses Python's standard library, so it does not need the MQTT packages. Run, using laptop A's actual IP address:

```powershell
python sensor.py --gateway-host 192.168.1.10
```

On B, open:

- Local sensing/camera page: `http://127.0.0.1:8091`
- Central dashboard on A: `http://192.168.1.10:8090`

Run only one sensor agent for these eight slot IDs at a time. The MQTT broker stays on laptop A's loopback interface; only the raw TCP sensor reports cross Wi-Fi. The central server subscribes locally. Campus access-point isolation can block laptop-to-laptop traffic, so a trusted hotspot may be easier.

A one-laptop run demonstrates the network software through loopback. It does not demonstrate Wi-Fi radio transmission. The two-laptop setup is what completes the wireless demonstration.

## Components and ports

| Component | File | Default interface and port |
|---|---|---|
| IoT sensor + local camera page | `sensor.py` | 127.0.0.1:8091 |
| Raw TCP gateway | `gateway.py` | 127.0.0.1:5050; LAN with --lan |
| MQTT broker | `broker.py` | 127.0.0.1:18884 |
| Central subscriber + dashboard | `server.py` | 127.0.0.1:8090; LAN with --lan |
| Launcher | `run_demo.py` | Starts the above as separate processes |
| Pixel comparison | `web/vision.js` | Runs in the camera browser |

These ports differ from the original project, which used 5000, 8080 and 8081. Close the old tabs and use the new addresses.

## Protocol

The sensor sends one compact JSON snapshot every second while readings are fresh. TCP messages end with newline and are bounded to 8192 bytes. An abbreviated example:

```json
{
  "source": "camera",
  "session": "sensor-session-identifier",
  "seq": 12,
  "slots": {"A01": true, "A02": false, "A03": false, "A04": false,
            "A05": false, "A06": false, "A07": false, "A08": false}
}
```

The gateway validates the eight known slot IDs and Boolean values. It adds a receive timestamp and publishes to **parking/v2/snapshot** using **MQTT QoS 1**, with retain disabled. The TCP acknowledgement means the broker acknowledged publication, not that the central application has already processed it. Seeing the corresponding sequence and payload on the central dashboard confirms subscriber processing.

The server ignores repeated or older sequence numbers within recent sessions. The gateway and central server run on the same machine in the supported configuration, so the gateway timestamp can reject delayed reports older than eight seconds. The server uses its own monotonic clock for freshness after receipt. Stale reports cannot make a disconnected slot appear free. Broker disconnection also marks availability unknown.

The first confirmed free slot in A01–A08 order is suggested. This is guidance, not reservation, shortest-path routing or AI prediction. If no space is confirmed free and some states are unknown, the UI shows uncertainty instead of claiming the parking area is full.

## Tests and troubleshooting

Run `python test_core.py`. See `TEST_RESULTS.md` for integration and browser checks performed during preparation.

- **Python can't open run_demo.py:** use the outer START_WINDOWS.bat, or enter the inner IntelligentParking folder first.
- **Missing amqtt / paho:** rerun INSTALL_WINDOWS.bat or `python -m pip install -r requirements.txt` using the interpreter used to launch.
- **Port already in use:** stop your previous automatic project terminal using Ctrl+C. The launcher lists any busy ports.
- **Camera access denied:** allow the browser permission, close other apps using the camera, and load the sensor page at localhost/127.0.0.1 on the camera laptop.
- **Slots stay unknown:** check the sensor status message, resume transmission, finish camera calibration, and keep the camera tab visible.
- **False camera occupancy:** remove objects, check lighting, recapture the empty reference, keep the camera fixed, or increase the changed-pixel threshold.
- **Wi-Fi failure:** verify the server IPv4 address, private-network firewall permissions, and whether the access point blocks peer communication.

## Scope

This is a classroom prototype for a trusted local network. It lacks authentication, TLS, persistent storage and reservations. Reports/history live in memory. Run one writer for the eight slots. The gateway is an educational protocol bridge that makes TCP programming and MQTT both directly observable; a production MQTT-capable sensor could publish straight to the broker. An ESP32 with IR/ultrasonic sensing could replace the camera agent after hardware development and calibration.

## References

- Python socket API: https://docs.python.org/3/library/socket.html
- Paho MQTT: https://eclipse.dev/paho/clients/python/docs/
- AMQTT broker configuration: https://amqtt.readthedocs.io/en/latest/references/broker_config/
- Browser camera access: https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
