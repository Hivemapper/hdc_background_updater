from typing import List


def get_rauc_status(lines: List) -> str:
    """
    Takes a list of lines read from stdout being produced by the "rauc install" command
    and produces a string suitable for setting in the rauc_state member of the Status class.

    See the "mock_rauc_[success|failed].sh" files to get an idea of what the RAUC
    stdout looks like.
    """

    in_progress = "in progress"
    success = "success"
    failed = "failed"

    if len(lines) == 0:
        return f"{in_progress}: starting"

    last_line = lines[-1]

    # Figure out if there is a % value in the string.
    percent_tokens = last_line.split("%")
    if len(percent_tokens) > 1:
        return f"{in_progress}: {percent_tokens[0]}%"

    if "succeeded" in last_line:
        return f"{success}"

    if "failed" not in last_line:
        return f"{in_progress}: pending"

    for line in lines:
        if "LastError: " not in line or "LastError: " != line[0:11]:
            continue

        return f"{failed}: {line[11:].lower()}"

    return f"{failed}"
