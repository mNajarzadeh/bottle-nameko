from types import SimpleNamespace
from bottle import Bottle
from bottle_nameko.plugin import NamekoPlugin
import json


def test_injects_client():
    client = object()
    plugin = NamekoPlugin(client=client)

    def handler(rpc):
        return rpc

    route = SimpleNamespace(callback=handler)
    wrapped = plugin.apply(handler, route) # better change
    assert wrapped() is client

def test_leaves_handler_without_rpc_unchanged():
    plugin = NamekoPlugin(client=object())

    def handler():
        return {"status": "ok"}

    route = SimpleNamespace(callback=handler)

    result = plugin.apply(handler, route)

    assert result is handler

def test_preserves_route_arguments():
    client = object()
    plugin = NamekoPlugin(client=client)

    def handler(name, rpc):
        return name, rpc

    route = SimpleNamespace(callback=handler)
    wrapped = plugin.apply(handler, route)

    name, received_client = wrapped(name="Ava")

    assert name == "Ava"
    assert received_client is client

def test_plugin_works_with_bottle():
    client = object()
    app = Bottle()
    app.install(NamekoPlugin(client=client))

    @app.get("/hello/<name>")
    def hello(name, rpc):
        assert rpc is client
        return {"message": f"Hello, {name}"}

    try:
        route = app.routes[0]
        result = route.call(name="Karim")

        assert json.loads(result) == {"message": "Hello, Karim"}
    finally:
        app.close()