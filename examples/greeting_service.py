from nameko.rpc import rpc


class GreetingService:
    name = "greeting"

    @rpc
    def hello(self, name):
        return f"Hello, {name}"