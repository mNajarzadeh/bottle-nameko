import json

from bottle import Bottle, HTTPResponse


class Gateway:
    def __init__(self, amqp_uri, timeout=5):
        self.amqp_uri = amqp_uri
        self.timeout = timeout
        self._app = Bottle()

    def get(self, path, **options):
        return self._app.get(path, **options)

    def run(self, host="127.0.0.1", port=8080):
        from nameko.exceptions import RpcTimeout
        from nameko.standalone.rpc import ClusterRpcProxy

        from .plugin import NamekoPlugin

        config = {"AMQP_URI": self.amqp_uri}

        def handle_rpc_timeout(callback):
            def wrapper(*args, **kwargs):
                try:
                    return callback(*args, **kwargs)
                except RpcTimeout:
                    return HTTPResponse(
                        body=json.dumps({
                            "error": "upstream_timeout",
                            "message": (
                                "The upstream service did not respond in time."
                            ),
                        }),
                        status=504,
                        content_type="application/json",
                    )

            return wrapper

        with ClusterRpcProxy(config, timeout=self.timeout) as client:
            plugin = NamekoPlugin(client=client)
            self._app.install(plugin)
            self._app.install(handle_rpc_timeout)

            try:
                self._app.run(host=host, port=port)
            finally:
                self._app.uninstall(handle_rpc_timeout)
                self._app.uninstall(plugin)