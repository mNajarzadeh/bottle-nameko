import eventlet

eventlet.monkey_patch()

from nameko.standalone.rpc import ClusterRpcProxy

from examples.gateway_app import create_app


def main():
    config = {
        "AMQP_URI": "amqp://dev:dev@rabbitmq:5672/",
    }

    with ClusterRpcProxy(config, timeout=5) as rpc:
        app = create_app(client=rpc)

        try:
            app.run(host="0.0.0.0", port=8080)
        finally:
            app.close()


if __name__ == "__main__":
    main()