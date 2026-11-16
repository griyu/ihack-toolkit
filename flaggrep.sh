#!/usr/bin/env bash
# CAPTURE-AND-REPLAY helper: pull flags out of traffic captures and logs.
# When another team exploits YOU, their attack is in your pcap/logs -- this
# finds the flags so you can see what's being stolen and reverse their exploit.
#
# Usage:
#   ./flaggrep.sh capture.pcap
#   ./flaggrep.sh /var/log/nginx/access.log
#   ./flaggrep.sh /path/to/dir   (greps everything under it)
#
# EDIT the FLAG pattern to match the real flag format (same as config.py).

FLAG='ihack\{\w{21}\}'      # iHack 2022 format; CONFIRM on the day and match config.py
# FLAG='[A-Z0-9]{31}='
# FLAG='flag\{[^}]*\}'

target="${1:?usage: $0 <pcap|logfile|dir>}"

if [[ "$target" == *.pcap || "$target" == *.pcapng ]]; then
    # extract readable strings from the capture, then grep
    if command -v tshark >/dev/null; then
        tshark -r "$target" -T fields -e data -e text 2>/dev/null \
            | strings | grep -oE "$FLAG" | sort -u
    fi
    strings "$target" | grep -oE "$FLAG" | sort -u
else
    grep -rhoE "$FLAG" "$target" 2>/dev/null | sort -u
fi
