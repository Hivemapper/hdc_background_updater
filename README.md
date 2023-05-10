# onboardupdater
This app is expected to be used on an embedded Linux system that uses the RAUC middleware to perform
firmware updates.

## Base Requirements
* `python3`
* `python3-pip`
* `python3-venv`

## Getting Started
1. Setup a virtual environment.  From the project root:
    ```
    python3 -m venv .venv
    source .venv/bin/activate
    ```
2. Install dependencies.
    ```
    python3 -m pip install -r requirements.txt
    ```
3. Run an integration test.
    ```
    python3 -m tests.integration
    ```
    Open a web browser and navigate to `http://localhost:8080/version`.  You should see some fake
    version data as JSON.

## API
The Onboard Updater (OU) uses a simple HTTP server run on port 8080.  The API can be fully exercised
on a localhost by running `python3 -m tests.integration`, though any calls to the RAUC middleware
are mocked.

### GET
* `version`

    This returns a JSON block of the version of the installed firmware.  See [representative version here](./tests/data/version.json).  Test via:
    ```
    curl -i -X GET http://localhost:8080/version
    ```

* `status`

    This returns a JSON block of the status of the OU.  See [the data structure here](./onboardupdater/status.py).
    Test via:
    ```
    curl -i -X GET http://localhost:8080/status
    ```
    * `rauc_state` is valid if the `state` field is set to `rauc_update`.
    * `last_error` is valid if the `state` field is set to `failed`.
    * `boot_state` is populated by an external client, not this app.

### POST
* `update`

    This triggers a firmware update.  The content of the POST should be a binary update file suitable for the RAUC
    middleware.  Test via (replacing the filepath):
    ```
    curl -i -X POST --data-binary @/tmp/rauc.update http://localhost:8080/update
    ```

* `cancel`

    This cancels an in-progress update if possible.

* `revert`

    This commands RAUC to mark the unused slot as the active slot and to reboot into that slot.

* `bootstate`

    This takes text/plain data and stores it in the `boot_state` field of the status object.  The purpose
    of this is that a boot test on the target may have status information that we want to provide to the user
    that can help to inform the health of the system and may drive the need to update the target.

    Test via:
    ```
    curl -i -X POST -H "Content-Type: text/plain" --data "healthy" http://localhost:8080/bootstate
    curl -i -X GET http://localhost:8080/status
    ```

### Logging
The Python logging module is used for basic logging, such as errors and state machine transitions.
[The configuration object](./onboardupdater/configuration.py) gives the expected location of the log file.
# hdc_background_updater
