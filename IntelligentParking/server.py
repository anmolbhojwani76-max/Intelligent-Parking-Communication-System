"""Central MQTT subscriber, live state, rolling history and HTTP dashboard."""

import argparse
import collections
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import paho.mqtt.client as mqtt
from common import SLOTS, TOPIC, STALE, validate

BASE = Path(__file__).parent


class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.seen = None
        self.slots = {s: False for s in SLOTS}
        self.source = None
        self.session = None
        self.seq = -1
        self.messages = 0
        self.duplicates = 0
        self.events = collections.deque(maxlen=60)
        self.history = collections.deque(maxlen=90)
        self.last_history = 0
        self.last_status = None
        self.last_payload = None
        self.sequences = collections.OrderedDict()

    def update(self, d):
        data = validate(d)
        at = d.get("gateway_at")
        if type(at) not in (int, float) or not 0 <= time.time() - at <= STALE:
            raise ValueError("Stale gateway report")
        with self.lock:
            key = data["session"]
            if data["seq"] <= self.sequences.get(key, -1):
                self.duplicates += 1
                return
            self.sequences[key] = data["seq"]
            self.sequences.move_to_end(key)
            while len(self.sequences) > 64:
                self.sequences.popitem(last=False)
            fresh = self.seen is not None and time.monotonic() - self.seen <= STALE
            for slot, occupied in data["slots"].items():
                if (
                    not fresh
                    or self.slots[slot] != occupied
                    or self.source != data["source"]
                ):
                    self.events.appendleft(
                        {
                            "time": time.strftime("%H:%M:%S"),
                            "slot": slot,
                            "state": "OCCUPIED" if occupied else "FREE",
                            "source": data["source"],
                        }
                    )
            self.slots = data["slots"]
            self.source = data["source"]
            self.session = key
            self.seq = data["seq"]
            self.seen = time.monotonic()
            self.messages += 1
            self.last_payload = data

    def snapshot(self, broker_connected):
        with self.lock:
            now = time.monotonic()
            age = None if self.seen is None else now - self.seen
            known = broker_connected and age is not None and age <= STALE
            rows = [
                {
                    "slot": s,
                    "status": (
                        ("OCCUPIED" if self.slots[s] else "FREE")
                        if known
                        else "UNKNOWN"
                    ),
                }
                for s in SLOTS
            ]
            counts = {
                status: sum(r["status"] == status for r in rows)
                for status in ("FREE", "OCCUPIED", "UNKNOWN")
            }
            if now - self.last_history >= 2:
                self.history.append({"time": time.strftime("%H:%M:%S"), **counts})
                self.last_history = now
            if self.last_status is True and not known:
                self.events.appendleft(
                    {
                        "time": time.strftime("%H:%M:%S"),
                        "slot": "ALL",
                        "state": "UNKNOWN",
                        "source": self.source or "none",
                    }
                )
            self.last_status = known
            return dict(
                slots=rows,
                counts=counts,
                source=self.source,
                age=None if age is None else round(age, 1),
                broker=broker_connected,
                live=known,
                messages=self.messages,
                duplicates=self.duplicates,
                seq=self.seq,
                session=self.session,
                recommendation=next(
                    (r["slot"] for r in rows if r["status"] == "FREE"), None
                ),
                events=list(self.events),
                history=list(self.history),
                payload=self.last_payload,
                topic=TOPIC,
            )


STATE = State()
CLIENT = None


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/state":
            b = json.dumps(STATE.snapshot(CLIENT.is_connected())).encode()
            mime = "application/json"
        elif self.path in ("/", "/index.html"):
            b = (BASE / "web/dashboard.html").read_bytes()
            mime = "text/html; charset=utf-8"
        elif self.path == "/style.css":
            b = (BASE / "web/style.css").read_bytes()
            mime = "text/css"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--bind", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8090)
    p.add_argument("--mqtt-port", type=int, default=18884)
    a = p.parse_args()
    CLIENT = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, client_id="parking-central-v2"
    )

    def connect(c, u, f, reason, props):
        if reason == 0:
            c.subscribe(TOPIC, qos=1)

    def message(c, u, msg):
        try:
            STATE.update(json.loads(msg.payload))
        except (ValueError, TypeError) as exc:
            print("Rejected report:", exc, flush=True)

    CLIENT.on_connect = connect
    CLIENT.on_message = message
    CLIENT.connect_async("127.0.0.1", a.mqtt_port, 30)
    CLIENT.loop_start()
    http = ThreadingHTTPServer((a.bind, a.port), Handler)
    print(f"Dashboard http://{a.bind}:{a.port}", flush=True)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        http.server_close()
        CLIENT.disconnect()
        CLIENT.loop_stop()
