#!/usr/bin/env sh

set -eu

write_line()
{
    echo "$@"
    sleep 0.2
}

write_line "installing"
write_line "  0% Installing"
write_line "  0% Determining slot states"
write_line " 20% Determining slot states done."
write_line " 20% Checking bundle"
write_line " 20% Verifying signature"
write_line " 40% Verifying signature done."
write_line " 40% Checking bundle done."
write_line " 40% Checking manifest contents"
write_line " 60% Checking manifest contents done."
write_line " 60% Determining target install group"
write_line " 80% Determining target install group done."
write_line " 80% Updating slots"
write_line " 80% Checking slot boot.0"
write_line " 85% Checking slot boot.0 done."
write_line " 85% Copying image to boot.0"
write_line " 90% Copying image to boot.0 done."
write_line " 90% Checking slot rootfs.0"
write_line " 95% Checking slot rootfs.0 done."
write_line " 95% Copying image to rootfs.0"
write_line "100% Copying image to rootfs.0 done."
write_line "100% Updating slots done."
write_line "100% Installing done."
write_line "Installing \`/tmp/update.raucb\` succeeded"

exit 0
