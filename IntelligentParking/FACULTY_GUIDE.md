# Demo notes

## Before starting

- Start the project and open the dashboard and sensor page side by side.
- For camera mode, keep the camera fixed above the parking board and calibrate with all eight spaces empty.
- For the Wi-Fi demo, connect two laptops and follow the [setup guide](README.md#connect-two-laptops-over-wi-fi).

## Demo sequence

1. Show the automatic simulation. The first car arrives after about five seconds.
2. Point out the occupied count, suggested free slot and received MQTT payload.
3. Switch to camera mode, capture an empty reference and start detection.
4. Place a toy car in A01. Check that it becomes occupied on the dashboard and that A02 is suggested.
5. Remove the car and check that A01 becomes free again.
6. Pause transmission. Wait for the last report to expire, then show the unknown states. Resume to show recovery.

Simulation uses generated readings. Camera mode detects changes in the physical scene. When stopping camera detection, allow about 15 seconds for both the sensor and server freshness timeouts.

## Presentation sections

Proposed speaking order:

| Member | Section |
|---|---|
| Anmol Bhojwani | Problem, objective and system architecture |
| Vedanth Dama | Camera sensing and calibration |
| Adyant Behera | TCP sockets and message validation |
| Mukunthan S | MQTT broker, topics and QoS |
| Shubham Gajanan Shinde | Wi-Fi setup, demo and conclusion |

## Points to understand

**TCP and MQTT:** The sensor sends newline-delimited JSON to the gateway using a TCP socket. The gateway validates it and publishes an MQTT message. MQTT also uses TCP, but adds the broker, topics and publish/subscribe model.

**Message boundaries:** TCP carries a byte stream. The newline marks the end of each JSON report.

**QoS 1:** MQTT provides at-least-once delivery between peers, so duplicates are possible. The server uses session and sequence numbers to reject repeated or older reports within tracked sessions.

**Acknowledgements:** The gateway replies after the MQTT broker acknowledges publication. The matching sequence on the dashboard confirms that the central subscriber processed the report.

**Failure handling:** Missing reports expire and the slots become unknown. Broker disconnection also marks availability unknown. Unknown slots are not recommended.

**Wireless communication:** With two laptops, sensor reports cross the Wi-Fi network. A single-laptop run uses loopback.

**Camera limits:** The detector compares the current scene with an empty reference. It can respond to shadows and other objects, so it does not recognise cars or number plates.

**Availability and reservations:** Two drivers can receive the same suggested space because the project does not reserve slots.

**Measurements:** Report age shows how long ago the server received a reading. It is not an end-to-end latency measurement. Fuel savings have not been measured.
