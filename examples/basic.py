from bottle import Bottle
from bottle_nameko.plugin import NamekoPlugin

class FakeClient:
    def hello(self, name):
        return f"Hello, {name}"

app = Bottle()
app.install(NamekoPlugin(client=FakeClient()))



@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/hello/<name>")
def hello(name, rpc):
    return {"message": rpc.hello(name)}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)