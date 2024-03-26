import re
from typing import Callable
import inspect

from sniffs.fixture import inject_fixtures, _RESERVED_FIXTURE_DICT
from sniffs.util import singleton


LHS_VARIABLE_TOKEN = "<"
RHS_VARIABLE_TOKEN = ">"
VARIABLE_OPTIONS_DELIMITER = ":"
LHS_OPTIONS_TOKEN = "{"
RHS_OPTIONS_TOKEN = "}"
OPTIONS_DELIMITER = ","


@singleton
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
                _func = route["handler"]
                _signature = inspect.signature(_func)
                _parameter_names = list(_signature.parameters)
                _all_available_kwargs = {
                    **match.groupdict(),
                    **_RESERVED_FIXTURE_DICT,
                }
                kwargs_to_pass = {
                    arg: value
                    for arg, value in _all_available_kwargs.items()
                    if arg in _parameter_names
                }  # Get only keyword arguments that exist in the function signature

                return _func(**kwargs_to_pass)

                # route["handler"](topic, message, match.groups(), match.groupdict())

    def _parse_topic_pattern(self, topic_pattern: str) -> re.Pattern:
        """
        Parse MQTT topic pattern and add named capture groups automatically.

        Args:
            topic_pattern (str): MQTT topic pattern.

        Returns:
            re.Pattern: Compiled regular expression pattern.
        """
        pattern_parts = []
        for part in topic_pattern.split("/"):
            # going to do some hand-wavy stuff for now, can validate things better later
            if LHS_OPTIONS_TOKEN in part and RHS_OPTIONS_TOKEN in part:
                variable_string, options_string = part.split(VARIABLE_OPTIONS_DELIMITER)
                variable = variable_string[1:-1]
                options_string = options_string[1:-1]
                options = options_string.split(OPTIONS_DELIMITER)
                options = [option for option in options if option]
                part = f"(?P<{re.escape(variable)}>{'|'.join(map(re.escape, options))})"
            elif part.startswith(LHS_VARIABLE_TOKEN) and part.endswith(
                RHS_VARIABLE_TOKEN
            ):
                variable = part[1:-1]
                part = f"(?P<{re.escape(variable)}>[^/]+)"
            pattern_parts.append(part)
        pattern = "/".join(pattern_parts)
        return re.compile(pattern)

    def reset(self):
        self.routes = []


def route(path):
    def decorator(func):
        Router().add_route(path, func)

        # @inject_fixtures
        # def wrapper(*args, **kwargs):
        #     return func(*args, **kwargs)

        # @inject_fixtures
        # def wrapper(topic, message, groups, named_groups):
        #     return func(topic, message, groups, named_groups)

        def wrapper(*args, **kwargs):
            # Get the signature of the wrapped function
            func_signature = inspect.signature(func)
            # Bind the provided arguments to the function signature
            bound_args = func_signature.bind(*args, **kwargs)
            # Pass only the arguments that are in the function signature
            return func(
                *[
                    bound_args.arguments[param.name]
                    for param in func_signature.parameters.values()
                ]
            )

        return wrapper

    return decorator
