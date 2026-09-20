# bottle-nameko

A Bottle plugin that injects a supplied RPC client into route handlers.

The repository includes a working HTTP-to-Nameko RPC example,
timeout handling, and automated tests.

## Current scope

The plugin injects the client into handlers that explicitly declare
an `rpc` parameter. Other handlers are left unchanged.

The application owns the client's lifecycle. Connection pooling
and concurrent RPC usage are not implemented or verified.

The example gateway converts Nameko RPC timeouts into HTTP 504 responses.
This error handling belongs to the example, not the plugin itself.

## Requirements

- Git
- Docker Engine with Docker Compose v2
- Available local ports: 5672, 15672, and 8080

The container example uses Python 3.10, Nameko 2.14.1,
Eventlet 0.40.3, and Bottle 0.13.4.

## Run the example

Clone the repository and enter its directory:

```bash
git clone https://github.com/mNajarzadeh/bottle-nameko.git
cd bottle-nameko
```

Run the following commands from the repository root.
If Docker requires elevated permissions on your system,
prefix Docker commands with `sudo`.

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

Wait for `starting services: greeting`, then press Ctrl+C
to stop following logs. The service keeps running.

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

## Plugin usage

With an initialized RPC client:

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

See `examples/gateway.py` for client startup, shutdown,
and Eventlet initialization.

Nameko is installed in the example containers.
Installing the plugin alone does not install Nameko.

## Tests

Build the test image and run the suite:

```bash
docker compose run --build --rm tests
```

For subsequent runs without dependency changes:

```bash
docker compose run --rm tests
```

The tests cover client injection, preservation of route arguments,
Bottle integration, successful gateway responses, and HTTP 504 handling.

Gateway tests use a mock client and do not require RabbitMQ.
Live RPC communication has been checked manually, not by this test suite.

GitHub Actions runs the suite on pushes and pull requests.

## Troubleshooting

Inspect service logs:

```bash
docker compose logs --tail=80 gateway greeting rabbitmq
```

The example initializes Eventlet before importing Bottle and Nameko.
Preserve this ordering in `examples/gateway.py`.

The gateway waits up to five seconds for an RPC reply.
A reply timeout returns HTTP 504, but does not cancel the remote task.
Broker connection failures are not covered by that timeout guarantee.

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

## Local development credentials

The example RabbitMQ username and password are both `dev`.
Its management interface is available at http://127.0.0.1:15672.

Published ports are bound to localhost.
These credentials are for the local example only.

## Stop the example

```bash
docker compose down
```

RabbitMQ data is not configured with a persistent volume.