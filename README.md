# iHack A&D starter toolkit + last-24-hours plan

Zero prep is fine — here's a realistic plan and ready scripts. The goal today is
**not** to learn all of security. It's to (1) understand and test these scripts,
(2) rehearse the exploit→patch→verify loop once, (3) rest. That alone puts you
ahead of most beginner teams.

> Reminder: AI tools (including Claude) are banned DURING the event. Setting
> these up today is prep. Tomorrow you run them yourself — so make sure all
> three of you understand what each script does. Read every file once.

## What's in here
| File | What it does |
| --- | --- |
| `config.py` | **Edit first on the day.** Flag format, team IPs, scoreboard submit settings, timing. Everything imports from here. |
| `exploit_template.py` | Copy per service. Fill in `exploit(ip)` to steal a flag from one target. |
| `runner.py` | Fires an exploit at every team each round, submits what it steals. Runs forever. |
| `submit.py` | Submits flags to the scoreboard, de-dupes, works over HTTP or TCP. |
| `flaggrep.sh` | Pulls flags out of pcaps/logs — for capture-and-replay. |
| `backup.sh` | Snapshot a service before patching (so you can undo). |
| `recon.sh` | `nmap` a box and remind you how to find dangerous code. |
| `setup.sh` | Run inside the Pwnbox: installs extras, Burp hint, tmux config. |
| `practice/` | A tiny vulnerable app + answer key to rehearse the whole loop today. |

## TODAY (Mon 16) — do this in order

**Step 1 — put it in a private git repo (20 min).**
Make a **private** GitHub/GitLab repo, drop this folder in, push it. Tomorrow you
`git clone` it into the Pwnbox in seconds. All three teammates get access.
```
cd ihack-toolkit
git init && git add . && git commit -m "starter toolkit"
# create a PRIVATE repo on github, then:
git remote add origin git@github.com:YOURNAME/ihack-toolkit.git
git push -u origin main
```

**Step 2 — rehearse the full loop on the practice app (90 min, together).**
```
pip install flask requests --break-system-packages
python3 practice/vuln_app.py      # terminal 1
```
In terminal 2, as a team:
1. **Recon:** `./recon.sh 127.0.0.1` and browse http://127.0.0.1:8080
2. **Attack:** find the flag (two bugs — see practice/README only if stuck).
   Put a working attack into a copy of the exploit template and test it:
   `cp exploit_template.py exploit_practice.py` then edit, then
   `./exploit_practice.py 127.0.0.1`
3. **Automate:** set `TEAM_IPS = ["127.0.0.1"]` in `config.py`, then
   `./runner.py exploit_practice` — watch it loop and "submit" (it'll error on
   submit until you set a real scoreboard; that's expected, you're testing flow).
4. **Patch:** `./backup.sh` the app dir, fix one bug in `vuln_app.py` (smallest
   change), restart, confirm your exploit now fails AND `/health` still says OK.
Doing this once end-to-end is the single most valuable hour you have.

**Step 3 — web speed drills (per person, 60–90 min).**
Each person does 3–4 PortSwigger Web Security Academy labs (SQL injection,
command injection, auth bypass, path traversal). Understanding the exploit is
what tells your defender where to patch.

**Step 4 — assign roles + logistics (30 min).**
- **Attacker** (strongest coder): owns exploits + the template.
- **Defender**: owns patching + SLA + backups.
- **Ops**: owns the box, tcpdump, submission, scoreboard, notes.
- Set up a private team chat + a shared notes doc.
- Charge devices, pack a LAN cable + USB-Ethernet adapter, confirm venue/time.

**Step 5 — sleep.** It's a 24h event. Don't cram past tonight.

## TOMORROW — first 10 minutes in the Pwnbox
1. `git clone` your repo. Run `./setup.sh`. Install Burp. Start tmux.
2. **Read the rules**: flag format, submit endpoint, round length, team IPs,
   your own IP. Fill them into `config.py`. Confirm `submit.py` posts a test flag.
3. Start capture: `sudo tcpdump -i any -w ~/cap.pcap &`
4. `./backup.sh` every service BEFORE touching anything.
5. Then: patch the obvious bugs (verify SLA stays green after each), get one
   exploit working, point `runner.py` at all teams, and watch your pcap with
   `flaggrep.sh` to steal others' exploits.

## The three rules that win as beginners
1. **Keep services UP.** Availability points are free and constant. Never break
   your own SLA chasing a fix — back up, small change, verify, or revert.
2. **Steal, don't invent.** Watch your traffic; replay attacks fired at you.
3. **Automate early.** One looping exploit > three clever manual ones.
