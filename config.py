"""
Central config for the whole toolkit. EDIT THIS FIRST on game day.
Everything else imports from here, so you change settings in one place.
"""
import re

# ---------------------------------------------------------------------------
# 1) FLAG FORMAT  -- get this from the rules/briefing on the day.
# Common A&D flags look like 31 chars + '='  e.g.  ABC123...=  (default below)
# Jeopardy-style often look like  flag{...}  or  iHack{...}
# Set the ONE that matches, then delete the others.
# ---------------------------------------------------------------------------
FLAG_REGEX = r"ihack\{\w{21}\}"   # iHack 2022 format: ihack{ + 21 chars }; CONFIRM at the briefing
# FLAG_REGEX = r"[A-Z0-9]{31}="
# FLAG_REGEX = r"flag\{[^}]+\}"
FLAG_RE = re.compile(FLAG_REGEX)

# ---------------------------------------------------------------------------
# 2) TEAMS  -- the list of target IPs. Fill from the scoreboard on the day.
# If the IPs follow a pattern like 10.60.<team>.1 use the helper below.
# ---------------------------------------------------------------------------
# Option A: explicit list
TEAM_IPS = [
    # "10.60.1.1",
    # "10.60.2.1",
]

# Option B: generate from a pattern (edit then uncomment)
# TEAM_IPS = [f"10.60.{i}.1" for i in range(1, 31)]

# YOUR OWN team IP(s) -- NEVER attack yourself. The runner skips these.
OUR_IPS = {
    # "10.60.7.1",
}

# FRIENDLY teams you choose NOT to attack (e.g. other teams from your uni).
# The runner skips every IP in here too. Attacking them is allowed by the
# rules and would score points -- this is purely your choice to sit them out.
# NOTE: they can still attack YOU, so keep defending against everyone.
FRIENDLY_IPS = {
    # "10.60.11.1",   # uni team 2
    # "10.60.12.1",   # uni team 3
    # "10.60.13.1",   # uni team 4
    # "10.60.14.1",   # uni team 5
}

# Everything the runner must never target = your box + friendly teams.
SKIP_IPS = OUR_IPS | FRIENDLY_IPS

# ---------------------------------------------------------------------------
# 3) SCOREBOARD SUBMISSION  -- how you submit stolen flags. Two common styles.
# Read the rules: it's usually an HTTP endpoint with a team token header,
# OR a raw TCP service you send flags to line by line.
# ---------------------------------------------------------------------------
SUBMIT_MODE = "http_bearer"   # "http_bearer" (iHack-style), "http" (generic), or "tcp"

# -- http_bearer: matches the iHack 2022 scoreboard (Bearer token + JSON {"flags":[...]}).
#    The 2022 endpoint looked like:
#      POST https://<scoreboard>/api/exercises/<uuid>/ctfad-submissions
#      Authorization: Bearer <token>   body: {"flags": ["ihack{...}"]}
SUBMIT_URL = "https://SCOREBOARD/api/exercises/UUID/ctfad-submissions"  # EDIT from briefing
SUBMIT_TOKEN = "YOUR_TEAM_BEARER_TOKEN"                                  # EDIT from briefing

# -- http (generic fallback): simple POST {"flag": ...} with a custom header --
SUBMIT_HEADER = "X-Team-Token"           # header name, EDIT if used

# -- tcp: send flags line by line to host:port --
SUBMIT_HOST = "scoreboard.ihack.local"   # EDIT
SUBMIT_PORT = 31337                        # EDIT

# ---------------------------------------------------------------------------
# 4) TIMING
# ---------------------------------------------------------------------------
ROUND_SECONDS = 300     # iHack 2022 tick was 5 min; tune to the real round length on the day
HTTP_TIMEOUT = 5        # per-request timeout when exploiting a target
MAX_WORKERS = 20        # parallel targets per round
