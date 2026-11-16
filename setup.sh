#!/usr/bin/env bash
# FIRST-MINUTES setup to run inside the Pwnbox on game day.
# The Pwnbox already has most tools; this installs the few extras + Burp,
# and sets a couple of quality-of-life things. Tweak freely.
set -uo pipefail

echo "[setup] python deps..."
pip install --quiet --break-system-packages requests pwntools 2>/dev/null || \
    pip install --quiet requests pwntools

echo "[setup] Burp Suite Community (if not present)..."
if ! command -v burpsuite >/dev/null 2>&1; then
    # adjust URL/version if needed; Pwnbox has outbound internet per the rules
    echo "  -> download Burp Community from https://portswigger.net/burp/releases"
    echo "     and run its installer, or use the Firefox already in the Pwnbox."
fi

echo "[setup] tmux quality of life..."
cat > ~/.tmux.conf <<'EOF'
set -g mouse on
set -g history-limit 50000
setw -g mode-keys vi
EOF

echo "[setup] done. Remember: start tcpdump and back up services next."
