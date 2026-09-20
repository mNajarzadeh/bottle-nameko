import argparse
from importlib import import_module
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Run a Bottle gateway for Nameko services."
    )
    parser.add_argument("application", help="Application as module:object")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    module_name, separator, object_name = args.application.partition(":")

    if not separator or not module_name or not object_name:
        parser.error("Use module:object, for example app:app")

    import eventlet

    eventlet.monkey_patch()

    from .gateway import Gateway

    sys.path.insert(0, str(Path.cwd()))
    module = import_module(module_name)
    application = getattr(module, object_name)

    if not isinstance(application, Gateway):
        parser.error("The application must be a Gateway instance")

    application.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()