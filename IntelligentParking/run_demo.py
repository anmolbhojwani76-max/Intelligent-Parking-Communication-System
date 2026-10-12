"""Start the real MQTT broker, subscriber, TCP gateway and automatic sensor."""

import argparse, importlib.util, socket, subprocess, sys, time, webbrowser
from pathlib import Path

BASE = Path(__file__).parent


def port_open(port):
    with socket.socket() as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) == 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--lan",
        action="store_true",
        help="Expose gateway and dashboard to trusted local Wi-Fi",
    )
    parser.add_argument(
        "--no-sensor",
        action="store_true",
        help="Run the sensor separately on a second laptop",
    )
    parser.add_argument("--no-browser", action="store_true")
    a = parser.parse_args()
    missing = []
    for mod in ["amqtt", "paho"]:
        if importlib.util.find_spec(mod) is None:
            missing.append(mod)
    if missing:
        print("Install dependencies first: python -m pip install -r requirements.txt")
        return 1
    ports = [18884, 5050, 8090] + ([] if a.no_sensor else [8091])
    busy = [str(p) for p in ports if port_open(p)]
    if busy:
        print(
            "Ports already in use: "
            + ", ".join(busy)
            + ". Stop an older demo before starting."
        )
        return 1
    bind = "0.0.0.0" if a.lan else "127.0.0.1"
    commands = [
        ["broker.py"],
        ["server.py", "--bind", bind],
        ["gateway.py", "--bind", bind],
    ]
    if not a.no_sensor:
        commands.append(["sensor.py"])
    children = []
    try:
        for args in commands:
            children.append(
                subprocess.Popen(
                    [sys.executable, str(BASE / args[0]), *args[1:]], cwd=BASE
                )
            )
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            if any(c.poll() is not None for c in children):
                raise RuntimeError("A component stopped. Read the error above.")
            if all(port_open(p) for p in ports):
                break
            time.sleep(0.3)
        else:
            raise RuntimeError("Startup timed out")
        print(
            "\nAutomatic parking system is running.\nDashboard: http://127.0.0.1:8090\n"
            + ("" if a.no_sensor else "Sensor station: http://127.0.0.1:8091\n")
            + "Press Ctrl+C here to stop all components.\n",
            flush=True,
        )
        if not a.no_browser:
            webbrowser.open("http://127.0.0.1:8090")
            if not a.no_sensor:
                webbrowser.open("http://127.0.0.1:8091")
        while all(c.poll() is None for c in children):
            time.sleep(0.5)
        raise RuntimeError(
            "A component stopped unexpectedly. Restart after checking the error above."
        )
    except KeyboardInterrupt:
        return 0
    except Exception as exc:
        print(exc)
        return 1
    finally:
        for c in children:
            if c.poll() is None:
                c.terminate()
        for c in children:
            try:
                c.wait(timeout=5)
            except subprocess.TimeoutExpired:
                c.kill()
                c.wait()


if __name__ == "__main__":
    sys.exit(main())
