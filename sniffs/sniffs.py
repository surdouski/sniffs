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

    def _on_connect(self, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print(
                f"Failed to connect: {reason_code}. loop_forever() will retry connection"
            )
        else:
            paths = self.router.get_topic_paths()
            for path in paths:
                self.client.subscribe(path)

    def _on_message(self, userdata, msg):
        self.router.route(msg.topic, msg.payload)
