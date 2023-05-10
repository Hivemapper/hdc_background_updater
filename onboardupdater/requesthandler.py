from http.server import BaseHTTPRequestHandler
from json import dumps, loads

from .configuration import Configuration
from .response import BadRouteResponse, NoDataResponse
from .staterunner import Response, StateRunner


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, config: Configuration, state_runner: StateRunner, *args):
        self.config = config
        self.state_runner = state_runner
        BaseHTTPRequestHandler.__init__(self, *args)

    def end_headers(self) -> None:
        self.send_header('Access-Control-Allow-Origin', '*')
        return super().end_headers()

    def do_GET(self):
        if self.path == "/version":
            self.respond(self.state_runner.get_version())
        elif self.path == "/status":
            self.respond(self.state_runner.get_status())
        else:
            self.respond(BadRouteResponse())

    def do_POST(self):
        if self.path == "/update":
            length = self.headers["content-length"]

            # length here is a string.
            if length is None or length == "0":
                self.respond(NoDataResponse())
                return

            data = self.rfile.read(int(length))
            self.respond(self.state_runner.post_update(data))
        elif self.path == "/cancel":
            self.respond(self.state_runner.post_cancel())
        elif self.path == "/revert":
            self.respond(self.state_runner.post_revert())
        elif self.path == "/bootstate":
            length = self.headers["content-length"]

            # length here is a string.
            if length is None or length == "0":
                # This isn't an error; it allows the client to clear out the state.
                data = ""
            else:
                data = self.rfile.read(int(length)).decode("utf-8")
            
            self.respond(self.state_runner.post_boot_state(data))
        else:
            self.respond(BadRouteResponse())

    def respond(self, response: Response) -> None:
        self.send_response(response.code)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        # Pretty print in case we're using curl or something to test.  All our
        # JSON is pretty minimal so this doesn't hurt.
        pretty_json = dumps(loads(response.json), indent=2)
        self.wfile.write(pretty_json.encode(encoding="utf_8"))
