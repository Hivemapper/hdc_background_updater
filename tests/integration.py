#!/usr/bin/env python3
#
# To run, from the project root, run "python3 -m tests.integration".

import logging

from onboardupdater.configuration import Configuration
from onboardupdater.onboardupdater import OnboardUpdater


if __name__ == "__main__":
    # This is meant to be a bit of a sandbox test, running the program on a dev computer.
    # As such we don't have the RAUC middleware to call so need to spoof those calls with
    # mock executables.  Commands are given as an array since that is how they are passed
    # to the subprocess module.
    config = Configuration()
    config.override_cmds = ["tests/rauc/mock_rauc_success.sh"]
    # config.override_cmds = ["tests/rauc/mock_rauc_failed.sh"]
    config.reboot_after_update = False
    config.revert_cmds = ["tests/rauc/mock_rauc_success.sh"]
    # config.revert_cmds = ["tests/rauc/mock_rauc_failed.sh"]
    config.update_cmds = ["tests/rauc/mock_rauc_update_success.sh"]
    # config.update_cmds = ["tests/rauc/mock_rauc_update_failed.sh"]
    config.update_write_path = "/tmp/update.rauc"
    config.version_path = "tests/data/version.json"

    logging.basicConfig(level=config.log_level)

    ou = OnboardUpdater(config)
    ou.start()
