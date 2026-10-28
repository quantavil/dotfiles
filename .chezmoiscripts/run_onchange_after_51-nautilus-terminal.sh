#!/bin/sh
set -eu
if gsettings list-schemas | grep -qx 'com.github.stunkymonkey.nautilus-open-any-terminal'; then
    gsettings set com.github.stunkymonkey.nautilus-open-any-terminal terminal rio
fi
