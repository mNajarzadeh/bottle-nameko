from bottle_nameko import Gateway

app = Gateway(
    amqp_uri="amqp://dev:dev@rabbitmq:5672/",
    timeout=5,
)


@app.get("/hello/<name>")
def hello(name, rpc):
    return {"message": rpc.greeting.hello(name)}