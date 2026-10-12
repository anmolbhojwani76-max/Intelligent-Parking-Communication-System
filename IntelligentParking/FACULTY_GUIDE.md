# Faculty demonstration and viva guide

## Opening explanation

“Our project monitors parking occupancy and sends it to a central server. It uses IoT sensing, raw TCP socket programming, MQTT publish/subscribe and, when run on two laptops, Wi-Fi communication. Occupancy changes are automatic. The dashboard is only a display.”

## Show the complete communication path

1. **IoT sensing:** show the source label. Camera mode obtains physical readings. Automatic simulation is a clearly labelled rehearsal source.
2. **TCP socket programming:** show `common.py` → `send_tcp`. Explain `socket.create_connection`, `sendall`, newline framing and the gateway response.
3. **MQTT:** show `gateway.py` → `publish` and `server.py` → `subscribe`. Explain the broker process, topic `parking/v2/snapshot`, QoS 1 and sequence numbers.
4. **Wireless networks:** if two laptops are available, the sensor on laptop B sends raw TCP packets to the gateway IP on laptop A over Wi-Fi.
5. **Central processing:** show the dashboard's received sequence, payload, arrival/departure log and occupancy graph.

## Demonstration sequence

- Start the project. Without touching any slots, watch a vehicle arrive after five seconds in automatic simulation. Explain that these are synthetic readings travelling through real network services.
- For the physical demonstration, switch to Camera detection, enable the webcam, align eight zones and capture the empty reference.
- Start detection and place a toy car in A01. Show the sensor overlay and central dashboard side by side. A01 becomes occupied and the suggestion changes to A02.
- Remove the object. A01 returns to free.
- Pause transmission. After more than eight seconds from the last report, the central dashboard marks all slots unknown. Resume to demonstrate recovery.
- Stop camera detection. Allow approximately fifteen seconds for agent freshness and central expiry. Unknown states prevent incorrect free-space guidance.

## Five-person speaking plan (suggested allocation)

| Member | Suggested section |
|---|---|
| Anmol Bhojwani | Problem, objective and complete architecture |
| Vedanth Dama | IoT sensing, calibration and automatic occupancy detection |
| Adyant Behera | TCP sockets, message framing and gateway validation |
| Mukunthan S | MQTT broker, topics, QoS and duplicate handling |
| Shubham Gajanan Shinde | Wi-Fi setup, live demo, failure recovery and conclusion |

This is a suggested presentation division, not a claim about who wrote which code.

## Short viva answers

**Why both TCP and MQTT?** The sensor uses a raw TCP application protocol to communicate with a gateway. The gateway translates validated reports into MQTT publications for subscribers. MQTT itself runs over TCP here, but its broker/topic mechanism is a separate application-level design.

**What makes it an IoT project?** A sensing node converts a physical observation into occupancy data and communicates it to another system. The camera is the physical sensor in camera mode. In simulation mode that sensing role is emulated.

**Is the system actually automatic?** After one-time camera calibration, changes are detected from video frames. No button sets a slot occupied or free. The automatic simulation also changes states on its own.

**What does the camera algorithm recognize?** It detects sustained visual differences in configured regions. It identifies occupancy/obstruction, not a specific car class. It works best with a fixed camera and controlled lighting.

**Why does TCP need newline framing?** TCP transports a byte stream and does not preserve application message boundaries. The newline tells the receiving code where the JSON snapshot ends.

**What does QoS 1 guarantee?** At least once delivery between MQTT peers. Duplicates can occur. Session/sequence tracking rejects duplicate or older snapshots at the central subscriber.

**What does a gateway acknowledgement prove?** The gateway validated the report and received the MQTT broker acknowledgement. The dashboard sequence confirms the central subscriber processed that report.

**What happens when the camera stops?** The sensor agent stops forwarding stale camera readings. The server eventually expires the last valid report and marks availability unknown.

**What if the broker fails?** The central subscriber reports broker disconnection and marks availability unknown. The gateway returns a failure instead of claiming successful delivery. Fresh reports restore the state after reconnect.

**Why not keep retained MQTT messages?** This prototype uses regular heartbeats and retain=false so it does not treat a previously retained snapshot as new evidence of availability.

**Are you measuring latency?** The UI shows the age of the last received report, not end-to-end latency. The project does not claim measured latency or fuel savings.

**How is Wi-Fi involved?** On two laptops, sensor TCP packets traverse the wireless LAN. A single-laptop localhost run uses loopback and cannot demonstrate radio communication.

**How would you deploy real hardware?** An ESP32 with a calibrated occupancy sensor can generate the same schema or publish MQTT directly. Authentication, encryption, persistent records and hardware validation are needed for deployment.

**Could two drivers receive the same recommendation?** Yes. The prototype shows availability. Preventing conflicting bookings requires reservation logic, which is outside this version.
