from copy import deepcopy
import logging
import os
import subprocess
import sys
from threading import RLock
import time

from transitions import Machine

from .configuration import Configuration
from .rauc import get_rauc_status
from .status import Status
from .trigger import Trigger

# https://github.com/pytransitions/transitions#states
states = [
    {
        "name": "ready",
        "on_enter": "on_enter_ready",
    },
    {
        "name": "write_update",
        "on_enter": "on_enter_write_update",
    },
    {
        "name": "rauc_update",
        "on_enter": "on_enter_rauc_update",
    },
    {
        "name": "override",
        "on_enter": "on_enter_override",
    },
    {
        "name": "failed",
        "on_enter": "on_enter_failed",
    },
    {
        "name": "revert",
        "on_enter": "on_enter_revert",
    },
    {
        "name": "reboot",
        "on_enter": "on_enter_reboot",
    },
]

# https://github.com/pytransitions/transitions#transitions
transitions = [
    # ready
    {
        "trigger": "update",
        "source": "ready",
        "dest": "write_update",
    },
    {
        "trigger": "revert",
        "source": "ready",
        "dest": "revert",
    },
    # write_update
    {
        "trigger": "write_update_success",
        "source": "write_update",
        "dest": "rauc_update",
    },
    {
        "trigger": "write_update_failed",
        "source": "write_update",
        "dest": "failed",
    },
    {
        "trigger": "cancel",
        "source": "write_update",
        "dest": "ready",
    },
    # rauc_update
    {
        "trigger": "rauc_update_success",
        "source": "rauc_update",
        "dest": "reboot",
    },
    {
        "trigger": "rauc_update_failed",
        "source": "rauc_update",
        "dest": "failed",
    },
    {
        "trigger": "cancel",
        "source": "rauc_update",
        "dest": "override",
    },
    # override
    {
        "trigger": "rauc_override_success",
        "source": "override",
        "dest": "ready",
    },
    {
        "trigger": "rauc_override_failed",
        "source": "override",
        "dest": "failed",
    },
    # failed
    {
        "trigger": "update",
        "source": "failed",
        "dest": "write_update",
    },
    # revert
    {
        "trigger": "rauc_revert_success",
        "source": "revert",
        "dest": "reboot",
    },
    {
        "trigger": "rauc_revert_failed",
        "source": "revert",
        "dest": "failed",
    },
    # reboot
    {
        "trigger": "return_to_ready",
        "source": "reboot",
        "dest": "ready",
    },
]


class Model(Machine):
    """
    This is the state machine model, inheriting from the transitions state machine class.
    Generally we do work on a state's entrance function.  A state can dictate subsequent
    transitions by posting a transition trigger back to the parent runner.

    Any access of the status object should be protected using the lock:  the state workers
    are called from the runner thread while the HTTP request handler thread queries
    the status object.
    """

    def __init__(self, config: Configuration, post_trigger):
        self.config = config
        self.post_trigger = post_trigger
        self.status = Status("ready")
        self.status_lock = RLock()

        Machine.__init__(
            self,
            initial="ready",
            states=states,
            transitions=transitions,
        )

    def get_status(self) -> Status:
        with self.status_lock:
            return deepcopy(self.status)

    def update_last_error(self, error: str) -> None:
        with self.status_lock:
            self.status.last_error = error

    def update_state(self) -> None:
        with self.status_lock:
            self.status.state = self.state

    def update_rauc_state(self, rauc_state: str) -> None:
        with self.status_lock:
            self.status.rauc_state = rauc_state

    def update_boot_state(self, boot_state: str) -> None:
        with self.status_lock:
            self.status.boot_state = boot_state

    def on_enter_ready(self, data: any) -> None:
        self.update_state()

    def on_enter_write_update(self, data: any) -> None:
        self.update_state()

        try:
            with open(self.config.update_write_path, "wb") as f:
                f.write(data)
                self.post_trigger(Trigger("write_update_success"))
        except OSError:
            logging.error(f"Unable to open '{self.config.update_write_path}' for writing")
            self.post_trigger(Trigger("write_update_failed", "unable to open file for writing"))
        except BaseException:
            logging.error(f"Unknown error trying to write update file {self.config.update_write_path}")
            self.post_trigger(Trigger("write_update_failed", "unknown error trying to write update file"))

    def on_enter_rauc_update(self, data: any) -> None:
        self.update_state()

        # RAUC writes most of its output to stdout but if it fails, then the failure message
        # goes to stderr.  Just put everything in stdout to make our parsing easier.
        process = subprocess.Popen(
            self.config.update_cmds + [self.config.update_write_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        lines = []
        return_code = None

        while True:
            output = process.stdout.readline()
            if output:
                line = output.strip().decode("utf-8")
                lines.append(line)

            self.update_rauc_state(get_rauc_status(lines))

            return_code = process.poll()
            if return_code is not None:
                sys.stdout.flush()
                for output in process.stdout.readlines():
                    line = output.strip().decode("utf-8")
                    lines.append(line)

                rauc_state = get_rauc_status(lines)
                self.update_rauc_state(rauc_state)

                if return_code == 0:
                    self.post_trigger(Trigger("rauc_update_success"))
                else:
                    logging.error(f"Error with RAUC update; {rauc_state}")
                    self.post_trigger(Trigger("rauc_update_failed", "error trying to install update"))
                break

            time.sleep(0.1)

    def on_enter_override(self, data: any) -> None:
        self.update_state()

        process = subprocess.run(self.config.override_cmds)

        if process.returncode == 0:
            self.post_trigger(Trigger("rauc_override_success"))
        else:
            self.post_trigger(Trigger("rauc_override_failed", "error trying to override update"))

    def on_enter_failed(self, data: any) -> None:
        self.update_state()
        self.update_last_error(data)

    def on_enter_revert(self, data: any) -> None:
        self.update_state()

        process = subprocess.run(self.config.revert_cmds)

        if process.returncode == 0:
            self.post_trigger(Trigger("rauc_revert_success"))
        else:
            self.post_trigger(Trigger("rauc_revert_failed", "error trying to revert to the other firmware"))

    def on_enter_reboot(self, data: any) -> None:
        self.update_state()
        time.sleep(self.config.reboot_sleep_time_s)

        if not self.config.reboot_after_update:
            # This is a special transition we only use for integration testing.
            self.post_trigger(Trigger("return_to_ready"))
        else:
            os.system(self.config.reboot_cmd)
