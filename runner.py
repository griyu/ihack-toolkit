#!/usr/bin/env python3
"""
ATTACK RUNNER -- the heart of your offense.

It imports an exploit module, fires it at EVERY team every round, collects the
flags, and hands them to submit.py. Runs forever until you Ctrl-C.

    ./runner.py exploit_webservice        # note: module name, no .py

Point it at different exploit modules as you build them. One reliable exploit
looping over all teams scores far more than clever one-off manual attacks.
"""
import sys
import time
import importlib
from concurrent.futures import ThreadPoolExecutor, as_completed

import config
from submit import submit_flags


def run_round(exploit_fn):
    targets = [ip for ip in config.TEAM_IPS if ip not in config.SKIP_IPS]
    all_flags = []
    with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as pool:
        futures = {pool.submit(exploit_fn, ip): ip for ip in targets}
        for fut in as_completed(futures):
            ip = futures[fut]
            try:
                flags = fut.result()
                if flags:
                    print(f"[+] {ip}: {len(flags)} flag(s)", file=sys.stderr)
                    all_flags += flags
            except Exception as e:
                print(f"[-] {ip}: {e}", file=sys.stderr)
    return all_flags


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <exploit_module>  (e.g. exploit_webservice)",
              file=sys.stderr)
        sys.exit(1)

    mod = importlib.import_module(sys.argv[1])
    exploit_fn = mod.exploit

    if not config.TEAM_IPS:
        print("[!] config.TEAM_IPS is empty -- fill in the team IPs first.",
              file=sys.stderr)
        sys.exit(1)

    rnd = 0
    while True:
        rnd += 1
        start = time.time()
        print(f"\n===== round {rnd} =====", file=sys.stderr)
        flags = run_round(exploit_fn)
        n = submit_flags(flags)
        print(f"[round {rnd}] {len(flags)} stolen, {n} new submitted",
              file=sys.stderr)
        # sleep the rest of the round
        elapsed = time.time() - start
        time.sleep(max(1, config.ROUND_SECONDS - elapsed))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[runner] stopped", file=sys.stderr)
