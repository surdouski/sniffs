# Sniffs - Python MQTT Router

Sniffs is a lightweight Python package for routing MQTT messages using flexible topic patterns. It provides an easy-to-use interface for defining routes and handling incoming messages efficiently.

## Features

- Define routes with dynamic topic patterns
- Support for named and unnamed placeholders in topic patterns
- Integration with MQTT clients for seamless message routing

## Installation

You can install Sniffs via pip:

```bash
pip install sniffs
```

## Usage

```python
import paho.mqtt.client as mqtt
import ssl
from sniffs import Sniffs

app = Sniffs()

@app.route("<key>:{option_1,option_2}/log")
def incredibly_broad_route(key, topic, message):
    print(f"key: {key}")
    print(f"topic: {topic}")
    print(f"message: {message}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="client123")
client.username_pw_set("username", "password")
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.connect(
    host="host",
    port=9937,
)

app.bind(client)

client.loop_forever()
```

## Documentation

### Named Placeholders

Placeholders can be used in your routes. For example, `room` here is used as a placeholder
and the argument name is injected into the function arguments:

```python
@app.route("<room>:{living_room,kitchen}/temperature")
def receive_temperature_data(room):
    if room == "living_room":
        # do something
    elif room == "kitchen":
        # do something else
```

Argument injection works by looking up the name of the placeholder, so using a different
name is the arguments will not work:

```python
# DOES NOT WORK, DO NOT DO THIS!!!
@app.route("<room>:{living_room,kitchen}/temperature")
def receive_temperature_data(argument_one):
    ...
```

### Wildcard Placeholders

If you want to match on anything, you can create a wildcard placeholder by not specifying any placeholder options.
This example effectively matches on the topic of `+/temperature`:

```python
@app.route("<room>/temperature")
def receive_temperature_data(room):
    ...
```

You can use any number of named and wildcard placeholders together:

```python
@app.route("<room>/<sensor>:{sensor_1,sensor_2}/<sensor_type>{temperature,humidity}")
def receive_temperature_data(room, sensor, sensor_type):
    ...
```

### `topic` and `message`

The `topic` and `message` arguments are injected, sort of like pytest fixtures. Do not use
them as your keys in your routes, as they are reserved.

`topic` - The topic on which the message was received. This will be the _actual_ topic name,
not the templated route. For instance, a route for `<room>:{living_room,kitchen}/temperature` will
always have a topic that is one of the following: `living_room/temperature`, `kitchen/temperature`.
This maps to the `on_message` function from paho mqtt client, with the value of `msg.topic`.

`message` - This maps to the `on_message` function, with the value of `msg.payload`.

```python
@app.route("<room>:{living_room,kitchen}/temperature")
def receive_temperature_data(room, topic, message):
    ...
```

The arguments are optional, they do not need to be included in your arguments:

```python
@app.route("<room>:{living_room,kitchen}/temperature")
def receive_temperature_data(room):
    ...
```

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
