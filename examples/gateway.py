import eventlet

eventlet.monkey_patch()
from bottle import Bottle
from nameko.standalone.rpc import ClusterRpcProxy

from bottle_nameko.plugin import NamekoPlugin


def main():
    config = {
        "AMQP_URI": "amqp://dev:dev@rabbitmq:5672/",
    }

    with ClusterRpcProxy(config, timeout=5) as rpc:
        app = Bottle()
        app.install(NamekoPlugin(client=rpc))

        @app.get("/hello/<name>")
        def hello(name, rpc):
            return {"message": rpc.greeting.hello(name)}

        try:
            app.run(host="0.0.0.0", port=8080)
        finally:
            app.close()


if __name__ == "__main__":
    main()