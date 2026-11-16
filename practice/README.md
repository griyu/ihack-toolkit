# Practice vulnbox — rehearsal answer key

Run `vuln_app.py`, then rehearse the **exploit → patch → verify** loop. Try the
attacks and fixes yourself before reading the answers below.

## Bug #1 — IDOR / missing authorization on `/note/<id>`
**Exploit:** just request other note IDs until you hit the flag.
```
curl "http://127.0.0.1:8080/note/42"
```
In `exploit_template.py`, loop `uid` over a range and regex the flag out (option (c)).

**Patch (smallest fix):** require the caller to own the note. Minimal version —
only serve notes owned by the authenticated user. For practice, restrict `/note`
to the legit owner and reject `system` notes:
```python
if n["owner"] == "system":
    return jsonify(error="forbidden"), 403
```
**Verify:** `/note/42` now 403s, but `/note/1` still returns alice's note and
`/health` still says OK. Service stays UP.

## Bug #2 — path traversal on `/read`
**Exploit:**
```
curl "http://127.0.0.1:8080/read?name=../vuln_app.py"
```
reads arbitrary files (in a real box, the flag file).

**Patch (smallest fix):** confine reads to a safe directory.
```python
import os
base = os.path.realpath("./safe")
path = os.path.realpath(os.path.join(base, os.path.basename(name)))
if not path.startswith(base):
    return jsonify(error="forbidden"), 403
```
or, simplest of all for practice, strip directory parts:
```python
name = os.path.basename(name)
```
**Verify:** traversal fails, legit filenames still work, `/health` OK.

## The point
Notice the rhythm every time: **back up first, make ONE small change, restart,
confirm the exploit fails AND the normal path + /health still work.** That rhythm
is exactly what you'll do on the real box tomorrow. If a patch ever breaks
`/health`, you'd be losing SLA — revert from backup and try a smaller fix.
