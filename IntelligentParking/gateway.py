"""Raw TCP input -> validated snapshot -> MQTT QoS 1 publication."""

import argparse
import json
import socketserver
import time
import paho.mqtt.client as mqtt
from common import TOPIC, MAX_MESSAGE, validate

CLIENT = None


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(4)
        try:
            line = self.rfile.readline(MAX_MESSAGE + 1)
            if len(line) > MAX_MESSAGE or not line.endswith(b"\n"):
                raise ValueError("Bounded newline-delimited JSON required")
            d = validate(json.loads(line))
            d["gateway_at"] = time.time()
            if not CLIENT.is_connected():
                raise OSError("MQTT broker disconnected")
            info = CLIENT.publish(TOPIC, json.dumps(d), qos=1, retain=False)
            info.wait_for_publish(timeout=2)
            if not info.is_published():
                raise OSError("MQTT broker did not acknowledge in time")
            reply = {
                "ok": True,
                "seq": d["seq"],
                "stage": "MQTT broker acknowledged",
                "topic": TOPIC,
            }
        except (ValueError, OSError, RuntimeError) as exc:
            reply = {"ok": False, "error": str(exc)}
        try:
            self.wfile.write(json.dumps(reply).encode() + b"\n")
        except OSError:
            pass


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--bind", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5050)
    p.add_argument("--mqtt-port", type=int, default=18884)
    a = p.parse_args()
    CLIENT = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, client_id="parking-gateway-v2"
    )
    CLIENT.connect_async("127.0.0.1", a.mqtt_port, 30)
    CLIENT.loop_start()
    server = Server((a.bind, a.port), Handler)
    print(f"TCP gateway on {a.bind}:{a.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        CLIENT.disconnect()
        CLIENT.loop_stop()
