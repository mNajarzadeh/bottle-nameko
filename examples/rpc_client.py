from nameko.standalone.rpc import ClusterRpcProxy

config = {
    "AMQP_URI": "amqp://dev:dev@rabbitmq:5672/",
}

with ClusterRpcProxy(config, timeout=5) as rpc:
    result = rpc.greeting.hello("Ali")
    print(result)