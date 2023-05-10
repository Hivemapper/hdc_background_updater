from json import dumps
import logging
from queue import Empty, SimpleQueue
from threading import RLock
import time

from transitions import MachineError

from .configuration import Configuration
from .model import Model
from .response import (
    InvalidCancelStateResponse,
    InvalidRevertStateResponse,
    InvalidUpdateStateResponse,
    NoVersionResponse,
    Response,
    SuccessResonse,
)
from .trigger import Trigger


class StateRunner:
    """
    This class maintains a queue of triggers to pass to the state machine model.  Some of those
    triggers come from the HTTP request handler (e.g. POST/update) but some of them also come
    from executing states in the state machine model itself after the state determines an
    operation was successful or failed.

    The class attempts to read the firmware version on start.  The version is protected by a
    lock since the HTTP request handler thread is going to query it.
    """

    def __init__(self, config: Configuration):
        self.config = config
        self.model = Model(config, self.post_trigger)
        self.triggers = SimpleQueue()
        self.version = ""
        self.version_lock = RLock()

    def execute(self) -> None:
        # Reading the version isn't actually in a state since it's a oneshot
        # at startup.
        self.read_version()

        while True:
            try:
                trigger = self.triggers.get(block=False)

                try:
                    self.model.trigger(trigger.name, trigger.data)
                except MachineError:
                    logging.error(f"Tried to trigger {trigger.name} from state {self.model.state}")
            except Empty:
                # This is common -- the queue is most likely empty.  We don't do it right now but
                # if any states needed a "tick" event we could put it here like so:
                #
                # if "tick" in self.model.get_triggers(self.model.state):
                #    self.model.trigger("tick", None)
                pass

            time.sleep(0.1)

    def get_status(self) -> Response:
        return Response(200, dumps(vars(self.model.get_status())))

    def get_version(self) -> Response:
        with self.version_lock:
            if self.version == "":
                return NoVersionResponse()

            return Response(200, self.version)

    def read_version(self) -> None:
        with self.version_lock:
            try:
                with open(self.config.version_path, "r") as f:
                    self.version = f.read()
            except OSError:
                logging.error(f"Unable to read version file at {self.config.version_path}")

    def post_trigger(self, trigger: Trigger) -> None:
        self.triggers.put(trigger)

    def post_update(self, data: bytes) -> Response:
        if "update" not in self.model.get_triggers(self.model.state):
            return InvalidUpdateStateResponse()

        self.triggers.put(Trigger("update", data))
        return SuccessResonse()

    def post_cancel(self) -> Response:
        if "cancel" not in self.model.get_triggers(self.model.state):
            return InvalidCancelStateResponse()

        self.triggers.put(Trigger("cancel"))
        return SuccessResonse()

    def post_revert(self) -> Response:
        if "revert" not in self.model.get_triggers(self.model.state):
            return InvalidRevertStateResponse()

        self.triggers.put(Trigger("revert"))
        return SuccessResonse()

    def post_boot_state(self, data: str) -> Response:
        self.model.update_boot_state(data)
        return SuccessResonse()
