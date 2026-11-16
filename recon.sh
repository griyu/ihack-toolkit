#!/usr/bin/env bash
# Quick recon of a target box (yours or a teammate's practice box).
# All boxes are identical, so scanning one tells you everyone's services.
#
# Usage: ./recon.sh 10.60.2.1
set -euo pipefail
ip="${1:?usage: $0 <ip>}"

echo "== nmap top ports =="
nmap -sV -T4 --top-ports 200 "$ip"

echo
echo "Next: for each open web port, browse it, grab the source off YOUR box,"
echo "and grep for dangerous sinks:"
echo "  rg -n 'system|exec|eval|pickle|subprocess|query|open\\(|include|require' ."
