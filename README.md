# Intelligent Parking Communication System

A Computer Networks project at SRM Institute of Science and Technology, Kattankulathur.

Finding a parking space often means driving around without knowing which slots are free. This project keeps track of eight parking slots and displays their availability on a central dashboard.

## Working

The sensor program sends slot readings to a gateway using TCP sockets. The gateway publishes the readings to an MQTT broker, and the central server receives them to update the dashboard.

There are two ways to run it:

- **Simulation:** cars arrive and leave automatically in a repeating sequence.
- **Camera:** a webcam observes marked parking spaces. After an empty reference is captured, changes in each space are used to detect occupancy.

The dashboard shows free, occupied and unknown slots and suggests the first available space. When readings stop, the affected availability expires instead of continuing to show an old value.

For the wireless demonstration, the sensor runs on one laptop and the server runs on another laptop connected to the same Wi-Fi network. This brings together socket programming, IoT, MQTT and wireless networks.

## Run the project

Install Python 3.10 or newer. Open the project folder in VS Code and run these commands in PowerShell, one at a time:

```powershell
.\INSTALL_WINDOWS.bat
.\START_WINDOWS.bat
```

The installer only needs to be run once. Wait for it to finish successfully before starting the project.

- Dashboard: http://127.0.0.1:8090
- Sensor page: http://127.0.0.1:8091

Simulation starts automatically. To use a webcam, select **Camera detection** on the sensor page, enable the camera, set the parking zones, capture the empty reference and start detection.

Keep the terminal open while running the project. Press **Ctrl+C** to stop it.

[Setup instructions, Wi-Fi connection and troubleshooting](IntelligentParking/README.md)

## Team

| Name | Registration number |
|---|---|
| Anmol Bhojwani | RA2411026011395 |
| Vedanth Dama | RA2411026011392 |
| Adyant Behera | RA2411026011384 |
| Mukunthan S | RA2411026011391 |
| Shubham Gajanan Shinde | RA2411026011394 |

**Faculty advisor:** Dr. Lakshmi Narayan  
Assistant Professor, Department of Computational Intelligence

## Current limitations

Camera mode detects visual changes, so shadows, hands and other objects may also register as occupied spaces. It works best with a fixed camera and steady lighting. The project does not reserve slots or recognise vehicle numbers.

This is a local-network prototype. Authentication, encryption and permanent storage are not included. Software checks are recorded in [TEST_RESULTS.md](IntelligentParking/TEST_RESULTS.md); the physical camera and two-laptop setup still need testing on the presentation equipment.
