#!/usr/bin/env sh

set -eu

write_line()
{
    echo "$@"
    sleep 0.5
}

write_error()
{
    >&2 echo "$@"
}

write_line "installing"
write_line "  0% Installing"
write_line "  0% Determining slot states"
write_line " 20% Checking bundle"
write_line " 40% Checking bundle failed."
write_line "100% Installing failed."
write_line "LastError: Signature size (12194220617738) exceeds bundle size"
# RAUC writes the final failure notification to stderr, not stdout.
write_error "Installing \`/tmp/update.raucb\` failed"

exit 1
