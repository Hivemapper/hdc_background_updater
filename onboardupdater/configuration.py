import logging


class Configuration:
    def __init__(self):
        # Leave hostname empty so that we bind to any network interface.
        self.hostname = ""
        self.log_level = logging.INFO
        self.log_path = "/tmp/onboardupdater.log"
        # Commands are tokenized so they can easily be used by the subprocess module.
        self.override_cmds = ["rauc", "status", "mark-active", "booted"]
        self.reboot_after_update = True
        # This is just passed to os.system so make it a single string rather than a list.
        # We expect this to be run under a non-root user so default to sudo.
        self.reboot_cmd = "sudo reboot"
        self.reboot_sleep_time_s = 2
        self.revert_cmds = ["rauc", "status", "mark-active", "other"]
        self.server_port = 8080
        self.update_cmds = ["rauc", "install"]
        self.update_write_path = "/tmp/update.raucb"
        self.version_path = "/etc/version.json"
