from types import SimpleNamespace
from unittest.mock import Mock

from nameko.exceptions import RpcTimeout
from webtest import TestApp

from examples.gateway_app import create_app


def test_hello_returns_service_response():
    hello = Mock(return_value="Hello, Ali")
    client = SimpleNamespace(
        greeting=SimpleNamespace(hello=hello)
    )
    app = create_app(client)

    try:
        response = TestApp(app).get("/hello/Ali", status=200)

        assert response.json == {"message": "Hello, Ali"}
        hello.assert_called_once_with("Ali")
    finally:
        app.close()


def test_hello_returns_504_on_rpc_timeout():
    hello = Mock(side_effect=RpcTimeout())
    client = SimpleNamespace(
        greeting=SimpleNamespace(hello=hello)
    )
    app = create_app(client)

    try:
        response = TestApp(app).get("/hello/Ali", status=504)

        assert response.json == {
            "error": "upstream_timeout",
            "message": "The greeting service did not respond in time.",
        }
        hello.assert_called_once_with("Ali")
    finally:
        app.close()