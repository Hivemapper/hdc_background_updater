from http.server import HTTPServer
import logging
import threading

from .configuration import Configuration
from .requesthandler import RequestHandler
from .staterunner import StateRunner


class OnboardUpdater:
    """
    This class creates the multi-threading model.  A worker thread is used to run the
    state machine while the main thread is given over to the HTTP server.
    """

    def __init__(self, config: Configuration):
        self.config = config
        self.state_runner = StateRunner(self.config)

        # Use this lambda as a way of passing data to the request handler.
        def request_handler(*args):
            RequestHandler(self.config, self.state_runner, *args)

        self.server = HTTPServer((config.hostname, config.server_port), request_handler)

    def start(self) -> None:
        # By setting daemon=True, the worker thread will be terminated automatically when the
        # main program thread terminates.
        x = threading.Thread(target=self.state_runner.execute, daemon=True)
        x.start()

        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            pass

        self.server.server_close()


def main() -> None:
    """
    This is the main entry point when running in a deployed system.
    """

    config = Configuration()

    logging.basicConfig(filename=config.log_path, level=config.log_level)

    ou = OnboardUpdater(config)
    ou.start()
