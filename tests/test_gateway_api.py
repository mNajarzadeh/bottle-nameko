from bottle_nameko import Gateway
from unittest.mock import patch

import pytest

from bottle_nameko.plugin import NamekoPlugin

from types import SimpleNamespace
from unittest.mock import Mock

from nameko.exceptions import RpcTimeout
from webtest import TestApp


def test_get_registers_route():
    gateway = Gateway(amqp_uri="amqp://localhost/")

    @gateway.get("/hello/<name>")
    def hello(name):
        return {"message": f"Hello, {name}"}

    route = gateway._app.routes[0]

    assert route.rule == "/hello/<name>"
    assert route.method == "GET"
    assert route.callback is hello

def test_run_cleans_up_when_server_fails():
    gateway = Gateway(amqp_uri="amqp://localhost/", timeout=5)
    error = RuntimeError("Server failed")

    with patch("nameko.standalone.rpc.ClusterRpcProxy") as proxy_class:
        connection = proxy_class.return_value
        connection.__exit__.return_value = False

        with patch.object(
            gateway._app,
            "run",
            side_effect=error,
        ) as run_server:
            with pytest.raises(RuntimeError, match="Server failed"):
                gateway.run(host="127.0.0.1", port=8080)

        proxy_class.assert_called_once_with(
            {"AMQP_URI": "amqp://localhost/"},
            timeout=5,
        )
        connection.__enter__.assert_called_once_with()
        connection.__exit__.assert_called_once()

        run_server.assert_called_once_with(
            host="127.0.0.1",
            port=8080,
        )

        assert not any(
            isinstance(plugin, NamekoPlugin)
            for plugin in gateway._app.plugins
        )


def test_gateway_returns_504_on_rpc_timeout():
    gateway = Gateway(amqp_uri="amqp://localhost/")
    hello = Mock(side_effect=RpcTimeout())
    client = SimpleNamespace(
        greeting=SimpleNamespace(hello=hello)
    )

    @gateway.get("/hello/<name>")
    def greeting(name, rpc):
        return {"message": rpc.greeting.hello(name)}

    def exercise_request(**options):
        response = TestApp(gateway._app).get(
            "/hello/Ali",
            status=504,
        )

        assert response.json == {
            "error": "upstream_timeout",
            "message": "The upstream service did not respond in time.",
        }
        hello.assert_called_once_with("Ali")

    original_plugins = list(gateway._app.plugins)

    with patch("nameko.standalone.rpc.ClusterRpcProxy") as proxy_class:
        connection = proxy_class.return_value
        connection.__enter__.return_value = client
        connection.__exit__.return_value = False

        with patch.object(
            gateway._app,
            "run",
            side_effect=exercise_request,
        ):
            gateway.run()

    assert gateway._app.plugins == original_plugins