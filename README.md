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

@app.route("<key>:{option_1,option_2}/log/#")
def incredibly_broad_route(location, topic, message):
    print(f"location: {location}")
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

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
