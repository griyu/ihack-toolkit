#!/usr/bin/env bash
# HUNT -- find attacker persistence + live intrusions on YOUR box.
# Run this every few minutes as defender. A past iHack winner's tactic was to
# root a box once, plant an SSH key + a hidden webshell, then just SSH in each
# tick to grab the flag. Patching the original bug does NOT remove that -- you
# have to hunt it down. Anything here you didn't put there is an intruder.
echo "==================== $(date) ===================="

echo "== [1] authorized_keys (remove any key your team didn't add) =="
for f in /root/.ssh/authorized_keys /home/*/.ssh/authorized_keys; do
  [ -f "$f" ] && { echo "--- $f ---"; cat "$f"; }
done

echo; echo "== [2] web files changed in the last 2h (webshell drops) =="
find /var/www /srv /app 2>/dev/null -type f -mmin -120 \
     -printf '%TY-%Tm-%Td %TH:%TM  %p\n' 2>/dev/null | sort

echo; echo "== [3] shell-like code in web roots (webshells) =="
grep -rIlE 'system\(|exec\(|passthru\(|shell_exec\(|popen\(|eval\(\$_' \
     /var/www /srv /app 2>/dev/null
find /var/www /srv /app 2>/dev/null \( -name '.*.php' -o -name '*.phtml' \) 2>/dev/null

echo; echo "== [4] listening ports (unexpected = backdoor) =="
ss -antlp 2>/dev/null

echo; echo "== [5] suspicious processes (reverse shells) =="
ps -aef --forest | grep -E 'nc |ncat|socat|/bin/sh|bash -i|python.*socket|perl.*socket' \
     | grep -v grep

echo; echo "== [6] cron jobs (persistence) =="
for u in $(cut -d: -f1 /etc/passwd); do
  crontab -l -u "$u" 2>/dev/null | grep -v '^\s*#' | sed "s/^/[$u] /"
done
cat /etc/cron.d/* /etc/crontab 2>/dev/null

echo; echo "== [7] who's logged in right now =="
w

echo; echo "[hunt] Review above. For anything you didn't create:"
echo "  - delete the rogue SSH key / webshell / cron line"
echo "  - kill the process:  kill -9 <pid>   (find cwd: ls -al /proc/<pid>)"
echo "  - THEN find and patch how they got root in the first place"
