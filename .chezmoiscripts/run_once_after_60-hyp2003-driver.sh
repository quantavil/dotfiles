#!/bin/sh
# Provision Hypersecu's HYP2003 PKCS#11 library for icegate-sign.
# The vendor binary is never stored in this repo; it is fetched from
# quantavil/hyp2003-linux-driver, checksum-verified, and copied once.
# Existing installs are never overwritten. No root, no vendor scripts.

dest="$HOME/.local/lib/hyp2003"
lib="$dest/libcastle_v2.so.1.0.0"

[ -f "$lib" ] && exit 0

tmp=$(mktemp -d) || exit 0
trap 'rm -rf "$tmp"' EXIT

if git clone --depth 1 -q https://github.com/quantavil/hyp2003-linux-driver "$tmp/src" 2>/dev/null \
    && (cd "$tmp/src" && sha256sum -c --quiet SHA256SUMS); then
    mkdir -p "$dest"
    install -m 644 "$tmp/src/libcastle_v2.so.1.0.0" "$lib"
    echo "hyp2003: installed $lib"
else
    echo "hyp2003: skipped (clone or checksum failed); rerun: chezmoi state delete-bucket --bucket=scriptState" >&2
fi
exit 0
