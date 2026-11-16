# iHack A&D — Command Cheat-Sheet

Commands only. Pwnbox = Linux. Fill `<...>` from the briefing.
Read on the box with:  `less CHEATSHEET.md`  (q to quit, / to search).

---

## 1. Setup + config
```bash
git clone <your-private-repo-url>     # or: cp -r /team/ihack-toolkit .
cd ihack-toolkit
bash setup.sh
tmux new -s ihack                     # others: tmux attach -t ihack
nano config.py                        # FLAG_REGEX, TEAM_IPS, OUR_IPS, FRIENDLY_IPS, SUBMIT_URL, SUBMIT_TOKEN
echo "<known-test-flag>" | ./submit.py
```

## 2. Monitor + recon
```bash
sudo tcpdump -i any -w ~/cap.pcap &         # capture everything
docker ps                                    # running services
docker logs -f <container> &                 # live logs
./recon.sh <any-team-ip>
docker inspect <container> | grep -A3 Mounts # where code lives
rg -n 'system|exec|eval|pickle|subprocess|query|open\(|include|require' <service-dir>
```
Extra recon:
```bash
nmap -sV -p- <ip>                            # full port + version scan
nmap -sV --top-ports 200 -T4 <ip>           # fast common ports
curl -i http://<ip>:<port>/                  # headers + body
curl -s http://<ip>:<port>/ | head -50       # peek at a page
ss -tlnp                                      # YOUR open ports + pids
ip a                                          # your interfaces / IP
cat /etc/hosts                                # names the game network uses
```

## 3. Defend: backup, patch, hunt
```bash
# BACK UP before touching anything
./backup.sh <service-dir>
./backup.sh <service-dir> <docker-volume>
docker commit <container> backup:<name>-$(date +%H%M)   # full snapshot
```
```bash
# PATCH, then restart ONLY that service, then verify UP
nano <service-dir>/<vulnerable-file>
docker compose restart <svc>
curl -s http://localhost:<port>/<health>
```
```bash
# REVERT if the patch broke it
rm -rf <service-dir> && cp -r ~/backups/<name>.ORIGINAL <service-dir>
docker compose restart <svc>
```
```bash
# HUNT persistence every few minutes (rogue keys, webshells, backdoors)
./hunt.sh
```
Baseline + tamper detection (catch files an attacker changed):
```bash
find <service-dir> -type f | xargs md5sum > ~/baseline.md5   # at game start
md5sum -c ~/baseline.md5 2>/dev/null | grep -v OK            # later: what changed
```

## 4. Attack: exploit, automate, replay
```bash
# build + test an exploit on YOUR OWN box first
cp exploit_template.py exploit_<svc>.py
nano exploit_<svc>.py              # fill exploit(ip), set PORT
./exploit_<svc>.py <your-own-ip>   # should print a flag
```
```bash
# automate against all teams (skips OUR_IPS + FRIENDLY_IPS)
./runner.py exploit_<svc>
```
```bash
# capture-and-replay: steal attacks fired at you
./flaggrep.sh ~/cap.pcap
# rebuild their request as exploit_<svc2>.py, then:
./runner.py exploit_<svc2>
```
Manual web attack probes (find the bug fast):
```bash
curl "http://<ip>:<port>/path?file=../../../../etc/passwd"    # path traversal
curl "http://<ip>:<port>/item?id=1'"                          # sqli error probe
curl -s "http://<ip>:<port>/?cmd=id"                          # command injection
ffuf -u http://<ip>:<port>/FUZZ -w /opt/wordlists/common.txt  # hidden endpoints
sqlmap -u "http://<ip>:<port>/item?id=1" --batch --dump       # auto sqli
```

## 5. Optional tools (pick ONE)
```bash
# DestructiveFarm -- flag farm (server once)
git clone https://github.com/DestructiveVoice/DestructiveFarm
cd DestructiveFarm/server
pip3 install -r requirements.txt
nano config.py          # TEAMS, FLAG_FORMAT, submit protocol/URL/token
./start_server.sh       # web UI :5000
cd ../client && ./start_sploit.py <exploit.py> -u http://<server-ip>:5000
```
```bash
# Tulip -- traffic analyzer (needs Docker)
git clone https://github.com/OpenAttackDefenseTools/tulip
cd tulip                # edit .env: flag regex, TICK_LENGTH, services, TRAFFIC_DIR
docker compose up -d    # UI http://localhost:3000 (keep on localhost only)
sudo tcpdump -i any -G 60 -w /traffic/cap-%H%M%S.pcap   # feed it
```

## 6. Incident-response one-liners
```bash
w                                   # who's logged in
ps -aef --forest                    # process tree
ss -antlp                           # listening ports + pids
lsof -i                             # what's using the network
kill -9 <pid>                       # kill intruder process
ls -al /proc/<pid>                  # a process's cwd (look for 'cwd ->')
cat /proc/<pid>/cmdline | tr '\0' ' '   # full command of a pid
tail -f /var/log/apache2/access.log # watch web hits for exploit patterns
tail -f /var/log/nginx/access.log   # (nginx variant)
grep -rn ihack /var/www /srv 2>/dev/null   # where the flag lives on disk
cat /root/.ssh/authorized_keys      # rogue SSH keys?
crontab -l ; cat /etc/crontab       # rogue cron jobs?
history                             # recent shell commands run on the box
```

## 7. Docker deep-dive
```bash
docker ps -a                         # all containers incl. stopped
docker exec -it <container> sh       # shell inside a container
docker exec <container> cat /flag    # peek a file inside
docker cp <container>:/app/file .    # pull a file out to edit
docker cp file <container>:/app/file # push an edited file back
docker compose logs -f <svc>         # follow a service's logs
docker compose build <svc> && docker compose up -d --force-recreate <svc>  # rebuild after editing baked-in source
docker stats                         # live CPU/RAM per container (watch for OOM)
docker inspect <container> | grep IPAddress   # container's internal IP
```

## 8. Reverse shells, listeners & pwn
```bash
nc -lvnp 4444                        # catch a reverse shell
socat file:`tty`,raw,echo=0 tcp-listen:4444   # better interactive listener
checksec --file=<binary>             # pwn: protections on a binary
strings <binary> | grep -i flag      # quick strings peek
file <binary>                        # what kind of binary
./<binary>                           # run it; or in gdb:  gdb ./<binary>
python3 -c 'from pwn import *; r=remote("<ip>",<port>); r.interactive()'
```

## 9. Encode / decode (fast)
```bash
echo -n 'text' | base64               # encode
echo 'dGV4dA==' | base64 -d           # decode
echo -n 'text' | md5sum               # hash
echo '41424344' | xxd -r -p           # hex -> bytes
python3 -c "import urllib.parse as u; print(u.quote('a b&c'))"   # url-encode
python3 -c "print(bytes.fromhex('deadbeef'))"
```

## 10. Blocking an attacker (USE WITH CARE)
```bash
# WARNING: blocking IPs can also block the scoreboard checker => you go DOWN.
# Prefer PATCHING over blocking. Only block a confirmed attacker, never broadly.
sudo iptables -A INPUT -s <attacker-ip> -j DROP     # block one IP
sudo iptables -L -n --line-numbers                  # list rules
sudo iptables -D INPUT <line-number>                # remove a rule (undo fast)
```

## 11. tmux + staying alive
```bash
tmux new -s ihack        # new session      | tmux attach -t ihack   # reattach
#   Ctrl-b c  new window      Ctrl-b "  split horizontal
#   Ctrl-b n  next window     Ctrl-b %  split vertical
#   Ctrl-b d  detach (leaves everything running)
nohup ./runner.py exploit_web &>> ~/runner.log &    # keep running if you disconnect
jobs ; fg %1              # see / foreground background jobs
```

## 12. Team access (shared box)
```bash
# add a teammate's public key so all 3 of you can work the box
echo "<teammate-pubkey>" >> ~/.ssh/authorized_keys
cp -r ~/ihack-toolkit /team/            # share via the /team folder
nano /team/notes.md                     # shared notes: IPs, bugs, patches, SLA
```
