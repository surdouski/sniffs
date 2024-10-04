import re
from typing import Callable
import inspect
import itertools

LHS_VARIABLE_TOKEN = "<"
RHS_VARIABLE_TOKEN = ">"
VARIABLE_OPTIONS_DELIMITER = ":"
LHS_OPTIONS_TOKEN = "{"
RHS_OPTIONS_TOKEN = "}"
OPTIONS_DELIMITER = ","


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
        self.routes.append(
            {
                "topic_pattern": pattern,
                "handler": handler,
                "unparsed_pattern": topic_pattern,
            }
        )

    def route(self, topic: str, message: str):
        """
        Route a received message to the appropriate handler based on the topic.

        Args:
            topic (str): MQTT topic of the received message.
            message (str): Payload of the received message.
        """
        results = []
        for route in self.routes:
            match = route["topic_pattern"].match(topic)
            if match:
                _func = route["handler"]
                _signature = inspect.signature(_func)
                _parameter_names = list(_signature.parameters)
                _all_available_kwargs = {
                    **match.groupdict(),
                    **{"topic": topic, "message": message},
                }
                kwargs_to_pass = {
                    arg: value
                    for arg, value in _all_available_kwargs.items()
                    if arg in _parameter_names
                }  # Get only keyword arguments that exist in the function signature

                results.append(_func(**kwargs_to_pass))
        return tuple(results) if len(results) else tuple()

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
        pattern = "/".join(pattern_parts) + "$"
        return re.compile(pattern)

    def get_topic_paths(self):
        return self._generate_subscription_topic_paths(
            [route["unparsed_pattern"] for route in self.routes]
        )

    def _generate_subscription_topic_paths(self, topic_patterns):
        generated_subscription_topics = []

        for path in topic_patterns:
            parts = path.split("/")
            variables = []
            for part in parts:
                if "<" in part and ">" in part:
                    var_name = part.replace("<", "").replace(">", "")
                    var_options = var_name.split(":")
                    if len(var_options) > 1:
                        path = path.replace(part, var_options[0])
                        variables.append(
                            (var_options[0], var_options[1].strip("{}").split(","))
                        )
                    else:
                        path = path.replace(part, var_name)
                        variables.append((var_name, ["+"]))

            combinations = itertools.product(*[options for _, options in variables])
            for combo in combinations:
                topic = path
                for (var_name, _), val in zip(variables, combo):
                    topic = topic.replace(f"{var_name}", val)
                generated_subscription_topics.append(topic)

        return generated_subscription_topics
