import logging
import functools
from typing import Any, Callable
import paho.mqtt.client as mqtt
from sniffs.router import Router


class Sniffs:
    """A dynamic wrapper for the paho mqtt client."""

    client: mqtt.Client
    router: Router

    def __init__(self, *args, **kwargs):
        self.router = Router()

    def bind(self, client: mqtt.Client):
        self.client = client
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def route(self, topic_pattern: str) -> Callable:
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            self.router.add_route(topic_pattern, func)
            return wrapper

        return decorator

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        # sometimes reason_code is an int, sometimes it's not. wonderful.
        code = None
        if isinstance(reason_code, int):
            code = reason_code
        else:
            code = reason_code.value
        if not (code == 0 or code == 1 or code == 2):
            print(
                f"Failed to connect: {reason_code}. loop_forever() will retry connection"
            )
        else:
            paths = self.router.get_topic_paths()
            for path in paths:
                client.subscribe(path)

    def _on_message(self, client, userdata, msg):
        self.router.route(msg.topic, msg.payload)
