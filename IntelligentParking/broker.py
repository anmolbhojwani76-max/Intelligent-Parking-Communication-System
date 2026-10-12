"""A real MQTT broker, bound to loopback for this classroom demonstration."""

import argparse
import asyncio
import logging
from amqtt.broker import Broker


async def serve(port):
    b = Broker(
        {
            "listeners": {"default": {"type": "tcp", "bind": f"127.0.0.1:{port}"}},
            "plugins": {
                "amqtt.plugins.authentication.AnonymousAuthPlugin": {
                    "allow_anonymous": True
                }
            },
        }
    )
    await b.start()
    print(f"MQTT broker listening on 127.0.0.1:{port}", flush=True)
    try:
        await asyncio.Future()
    finally:
        await b.shutdown()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=18884)
    a = p.parse_args()
    logging.basicConfig(level=logging.ERROR)
    try:
        asyncio.run(serve(a.port))
    except KeyboardInterrupt:
        pass
