import re
from typing import Callable


class Router:
    def __init__(self):
        self.routes = []

    def add_route(self, topic_pattern: str, handler: Callable):
        """
        Add a route to the router.

        Args:
            topic_pattern (str): MQTT topic pattern to match.
            handler (Callable): Handler function to be called when a message is received on the matched topic.
        """
        # Parse the topic pattern to automatically add named capture groups
        pattern = self._parse_topic_pattern(topic_pattern)
        self.routes.append({"topic_pattern": pattern, "handler": handler})

    def route(self, topic: str, message: str):
        """
        Route a received message to the appropriate handler based on the topic.

        Args:
            topic (str): MQTT topic of the received message.
            message (str): Payload of the received message.
        """
        for route in self.routes:
            match = route["topic_pattern"].match(topic)
            if match:
                route["handler"](topic, message, match.groups())

    def _parse_topic_pattern(self, topic_pattern: str) -> re.Pattern:
        """
        Parse MQTT topic pattern and add named capture groups automatically.

        Args:
            topic_pattern (str): MQTT topic pattern.

        Returns:
            re.Pattern: Compiled regular expression pattern.
        """
        # Replace "+:<variable>" with named capture groups
        pattern_parts = []
        for part in topic_pattern.split("/"):
            if part.startswith("{") and part.endswith("}"):
                variables_string = part[1:-1]  # remove { }
                variables = [
                    variable for variable in variables_string.split(",") if variable
                ]  # gather names into a list and remove any empty strings
                part = f"({'|'.join(map(re.escape, variables))})"
            elif part == "+":
                part = f"([^/]*)"
            pattern_parts.append(part)
        pattern = "/".join(pattern_parts)
        return re.compile(pattern)
