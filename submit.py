#!/usr/bin/env python3
"""
Flag submitter. Sends flags to the scoreboard and remembers what it already
sent so you never submit a duplicate.

Use it two ways:
  1) As a command, piping flags in (one per line):
        cat flags.txt | ./submit.py
        ./exploit_template.py 10.60.2.1 | ./submit.py
  2) Imported by runner.py:
        from submit import submit_flags
        submit_flags(["ABC...=", "DEF...="])

Flags usually EXPIRE each round, so submit immediately -- don't collect.
"""
import sys
import socket
import requests
import config

# scoreboards often use self-signed HTTPS; quiet the warning
try:
    requests.packages.urllib3.disable_warnings()
except Exception:
    pass

_SEEN = set()           # in-memory dedupe for this process
_SEEN_FILE = "submitted_flags.txt"

# load previously submitted flags from disk so restarts don't resubmit
try:
    with open(_SEEN_FILE) as f:
        _SEEN.update(line.strip() for line in f if line.strip())
except FileNotFoundError:
    pass


def _remember(flag):
    _SEEN.add(flag)
    with open(_SEEN_FILE, "a") as f:
        f.write(flag + "\n")


def _submit_http(flag):
    try:
        r = requests.post(
            config.SUBMIT_URL,
            headers={config.SUBMIT_HEADER: config.SUBMIT_TOKEN},
            json={"flag": flag},
            timeout=config.HTTP_TIMEOUT,
        )
        return f"{r.status_code} {r.text.strip()[:80]}"
    except Exception as e:
        return f"ERR {e}"


def _submit_http_bearer(flag):
    # iHack-style: Authorization: Bearer <token> + JSON body {"flags": [flag]}
    try:
        r = requests.post(
            config.SUBMIT_URL,
            headers={
                "Authorization": f"Bearer {config.SUBMIT_TOKEN}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json={"flags": [flag]},
            timeout=config.HTTP_TIMEOUT,
            verify=False,
        )
        return f"{r.status_code} {r.text.strip()[:80]}"
    except Exception as e:
        return f"ERR {e}"


def _submit_tcp(flag):
    try:
        with socket.create_connection(
            (config.SUBMIT_HOST, config.SUBMIT_PORT), timeout=config.HTTP_TIMEOUT
        ) as s:
            s.sendall((flag + "\n").encode())
            return s.recv(256).decode(errors="replace").strip()[:80]
    except Exception as e:
        return f"ERR {e}"


def submit_flags(flags):
    """Submit a list/iterable of flags. Returns count of newly-submitted."""
    new = 0
    for flag in flags:
        flag = flag.strip()
        if not flag or flag in _SEEN:
            continue
        if config.SUBMIT_MODE == "tcp":
            resp = _submit_tcp(flag)
        elif config.SUBMIT_MODE == "http_bearer":
            resp = _submit_http_bearer(flag)
        else:
            resp = _submit_http(flag)
        _remember(flag)
        new += 1
        print(f"[submit] {flag[:20]}... -> {resp}", file=sys.stderr)
    return new


if __name__ == "__main__":
    # read flags from args or stdin
    flags = sys.argv[1:] if len(sys.argv) > 1 else sys.stdin
    n = submit_flags(flags)
    print(f"[submit] {n} new flag(s) submitted", file=sys.stderr)
