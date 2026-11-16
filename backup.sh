#!/usr/bin/env bash
# BACKUP before you patch -- works for plain dirs AND Docker services.
# If a patch breaks the service (DOWN = lost SLA), restore in seconds.
#
# Usage:
#   ./backup.sh /srv/webservice                 # back up a source directory
#   ./backup.sh /srv/webservice vol1 vol2       # dir + named docker volumes
#
# Restore a dir later:
#   rm -rf /srv/webservice && cp -r ~/backups/webservice.ORIGINAL /srv/webservice
# Restore a docker volume later (example):
#   docker run --rm -v vol1:/v -v ~/backups:/b alpine \
#       sh -c "rm -rf /v/* && tar xzf /b/vol1.ORIGINAL.tgz -C /v"
set -uo pipefail

src="${1:?usage: $0 <service-dir> [docker-volume ...]}"
shift || true
name="$(basename "$src")"
dest=~/backups
mkdir -p "$dest"

# --- source directory: one pristine ORIGINAL + a timestamped snapshot ---
if [[ -e "$src" ]]; then
    [[ -e "$dest/$name.ORIGINAL" ]] || { cp -r "$src" "$dest/$name.ORIGINAL"; \
        echo "[backup] pristine dir -> $dest/$name.ORIGINAL"; }
    stamp="$(date +%H%M%S)"
    cp -r "$src" "$dest/$name.$stamp"
    echo "[backup] snapshot dir -> $dest/$name.$stamp"
else
    echo "[backup] note: '$src' not found on disk (maybe it's inside a container)"
fi

# --- optional docker volumes: tar each into ~/backups ---
for vol in "$@"; do
    if [[ ! -e "$dest/$vol.ORIGINAL.tgz" ]]; then
        docker run --rm -v "$vol":/v -v "$dest":/b alpine \
            tar czf "/b/$vol.ORIGINAL.tgz" -C /v . \
            && echo "[backup] pristine volume -> $dest/$vol.ORIGINAL.tgz"
    fi
    docker run --rm -v "$vol":/v -v "$dest":/b alpine \
        tar czf "/b/$vol.$(date +%H%M%S).tgz" -C /v . \
        && echo "[backup] snapshot volume -> $dest/$vol.<time>.tgz"
done

echo "[backup] done. Tip: also 'docker ps' and note image names so you can"
echo "         'docker commit <container> backup:<name>' for a full snapshot."
