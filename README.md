# bottle-nameko

Build a Bottle HTTP gateway for Nameko RPC services with a small Python file.

Requires Python 3.10, a running RabbitMQ broker, and a Nameko service.

## Installation

Requires Python 3.10.

```bash
python -m pip install bottle-nameko
```

Nameko and the other runtime dependencies are installed automatically.

See the [PyPI package page](https://pypi.org/project/bottle-nameko/).

## Quick start

Create `app.py`:

```python
from bottle_nameko import Gateway

app = Gateway(
    amqp_uri="amqp://dev:dev@localhost:5672/",
    timeout=5,
)


@app.get("/hello/<name>")
def hello(name, rpc):
    return {"message": rpc.greeting.hello(name)}
```

Run from the directory containing `app.py`:

```bash
bottle-nameko app:app
```

Send a request:

```bash
curl -i http://127.0.0.1:8080/hello/Ali
```

Expected status: HTTP 200.

```json
{"message": "Hello, Ali"}
```

This example expects a Nameko service named `greeting` with an RPC
method named `hello`. Replace the broker URL and service call with
those of your own environment.

The command initializes Eventlet before loading your application.
The gateway manages the RPC client lifecycle and injects the client
into handlers that explicitly declare an `rpc` parameter.

An RPC reply timeout returns HTTP 504:

```json
{
  "error": "upstream_timeout",
  "message": "The upstream service did not respond in time."
}
```

A timeout does not cancel the remote task.

## Command-line options

```bash
bottle-nameko app:app --host 127.0.0.1 --port 8080
```

- `app:app`: Python module name followed by the Gateway object name.
- `--host`: Listening address; defaults to `127.0.0.1`.
- `--port`: Listening port; defaults to `8080`.

## Current limitations

- Python 3.10 is the currently supported runtime.
- The Gateway API currently exposes GET routes.
- Concurrent RPC usage has not been verified.
- Connection pooling is not implemented.
- Broker connection failures are not covered by the RPC reply timeout.
- The bundled server is intended for local development.

## Run the Docker example

The repository includes a greeting service, RabbitMQ, and a gateway.

### Requirements

- Git
- Docker Engine with Docker Compose v2
- Available local ports: 5672, 15672, and 8080

Docker is needed for this example, not for installing the Python package.

The example uses Python 3.10, Nameko 2.14.1, Eventlet 0.40.3,
and Bottle 0.13.4.

### Setup

Clone the repository:

```bash
git clone https://github.com/mNajarzadeh/bottle-nameko.git
cd bottle-nameko
```

Until the Gateway changes are merged into `main`, switch to:

```bash
git switch feat/simple-gateway
```

Run the following commands from the repository root.
If Docker requires elevated permissions, prefix Docker commands with `sudo`.

Start RabbitMQ:

```bash
docker compose up -d rabbitmq
```

Check readiness:

```bash
docker compose exec rabbitmq rabbitmq-diagnostics -q ping
```

Wait until this reports `Ping succeeded` before continuing.
Compose startup ordering alone does not guarantee readiness.

Build and start the greeting service:

```bash
docker compose up -d --build greeting
docker compose logs -f greeting
```

Wait for `starting services: greeting`, then press Ctrl+C to stop
following logs. The service keeps running.

Start the gateway:

```bash
docker compose up -d --build gateway
```

Send a request:

```bash
curl -i --max-time 12 http://127.0.0.1:8080/hello/Ali
```

Expected status: HTTP 200.

```json
{"message": "Hello, Ali"}
```

Request flow:

```text
HTTP client → Bottle gateway → RabbitMQ → Nameko greeting service
```

### Local credentials

The example RabbitMQ username and password are both `dev`.

The management interface is available at:

http://127.0.0.1:15672

Published ports are bound to localhost.
These credentials are for the local example only.

### Stop the example

```bash
docker compose down
```

RabbitMQ data is not configured with a persistent volume.

## Direct plugin usage

For an existing Bottle application, supply an initialized RPC client:

```python
from bottle import Bottle
from bottle_nameko.plugin import NamekoPlugin


def create_app(client):
    app = Bottle()
    app.install(NamekoPlugin(client=client))

    @app.get("/hello/<name>")
    def hello(name, rpc):
        return {"message": rpc.greeting.hello(name)}

    return app
```

The plugin leaves handlers without an explicit `rpc` parameter unchanged.

When using `NamekoPlugin` directly, your application is responsible
for the client's lifecycle, execution environment, and error handling.
Automatic HTTP 504 handling is provided by the Gateway runner,
not by the injection plugin itself.

## Tests

Build the test image and run the suite:

```bash
docker compose run --build --rm tests
```

For subsequent runs without dependency changes:

```bash
docker compose run --rm tests
```

Tests cover client injection, route arguments, Bottle integration,
gateway responses, RPC timeout handling, and cleanup when the server fails.

Gateway tests use mock clients and do not require RabbitMQ.
Live RPC communication has been checked manually, not by this test suite.

GitHub Actions runs the suite on pushes and pull requests.

## Troubleshooting

Inspect service logs:

```bash
docker compose logs --tail=80 gateway greeting rabbitmq
```

Use the `bottle-nameko` command to run an installed application.
It initializes Eventlet before importing Bottle, Nameko, and your
application module.

The Docker example uses the equivalent module entry point:

```bash
python -m bottle_nameko.cli examples.simple_gateway:app --host 0.0.0.0
```

If requests hang, check the startup logs and confirm that both RabbitMQ
and the greeting service are ready.

The example waits up to five seconds for an RPC reply.
This is not an overall deadline for broker connection and reconnection.

After changing the greeting service, rebuild its image:

```bash
docker compose up -d --build greeting
```

After changing gateway or plugin code, restart the gateway:

```bash
docker compose restart gateway
```

The gateway mounts the repository read-only, so these code changes
do not require an image rebuild.

After changing Compose configuration, apply it with:

```bash
docker compose up -d gateway
```