from bottle import Bottle, response
from nameko.exceptions import RpcTimeout

from bottle_nameko.plugin import NamekoPlugin


def create_app(client):
    app = Bottle()
    app.install(NamekoPlugin(client=client))

    @app.get("/hello/<name>")
    def hello(name, rpc):
        try:
            message = rpc.greeting.hello(name)
        except RpcTimeout:
            response.status = 504
            return {
                "error": "upstream_timeout",
                "message": "The greeting service did not respond in time.",
            }

        return {"message": message}

    return app