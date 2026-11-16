#!/usr/bin/env python3
"""
PRACTICE VULNBOX (for rehearsal only -- NOT for the real event).

A tiny Flask service that mimics an A&D challenge: it stores a "flag" and has
TWO planted bugs. Use it to rehearse the full loop today:
    recon -> find bug -> write exploit -> run it -> PATCH it -> verify still up.

Run it:
    pip install flask --break-system-packages
    python3 vuln_app.py
Then it listens on http://127.0.0.1:8080

WORKFLOW TO PRACTICE
  1. Attacker: find a way to read the flag (two different bugs exist).
     Put your working attack into ../exploit_template.py and test:
        ../exploit_template.py 127.0.0.1
  2. Defender: open THIS file, fix the bug with the smallest change,
     restart, and confirm (a) the exploit now fails, (b) /health still says OK
     and the normal /note/1 still works for the legit user.
  3. Repeat for the second bug.

Answer key is in practice/README.md -- don't peek until you've tried.
"""
from flask import Flask, request, jsonify

app = Flask(__name__)

# the "flag" the checker would plant each round
FLAG = "PRACTICEFLAG0000000000000000000="

# fake notes store; note 1 is the legit user's, note 42 secretly holds the flag
NOTES = {
    "1": {"owner": "alice", "text": "buy milk"},
    "42": {"owner": "system", "text": FLAG},
}


@app.route("/health")
def health():
    # the checker hits this; if it ever stops returning OK you're "DOWN"
    return "OK"


@app.route("/note/<nid>")
def note(nid):
    # BUG #1 (IDOR / missing authorization): returns ANY note by id with no
    # check that the caller owns it -> attacker reads note 42 and gets the flag.
    n = NOTES.get(nid)
    if not n:
        return jsonify(error="not found"), 404
    return jsonify(owner=n["owner"], text=n["text"])


@app.route("/read")
def read_file():
    # BUG #2 (path traversal): reads whatever file you name, no sanitisation.
    # e.g. /read?name=../vuln_app.py  (or point it at a flag file in the real one)
    name = request.args.get("name", "")
    try:
        with open(name) as f:            # <-- dangerous: no path restriction
            return f.read()
    except Exception as e:
        return jsonify(error=str(e)), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
