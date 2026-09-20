from inspect import signature

class NamekoPlugin:
    name = "nameko"
    api = 2

    def __init__(self, client):
        self.client = client

    def apply(self, callback, route):
        parameters = signature(route.callback).parameters

        if "rpc" not in parameters:
            return callback

        def wrapper(*args, **kwargs):
            kwargs["rpc"] = self.client
            return callback(*args, **kwargs)

        return wrapper