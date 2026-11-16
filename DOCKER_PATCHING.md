# Patching a Docker service without breaking SLA

Your pwnbox preview shows `docker ready`, so services most likely run as
containers. Patching a container is a slightly different rhythm than editing a
plain file. Same golden rule: **back up, smallest change, restart, verify still
UP.** Rehearse this today so it's automatic tomorrow.

## 1. See what's running
```bash
docker ps                      # containers, names, ports
docker compose ps              # if the service uses docker-compose
```
Note each service's container name and the port it exposes.

## 2. Find where the code lives (two common cases)

**Case A - source is mounted from the host (easiest).** Look at the mounts:
```bash
docker inspect <container> | grep -A3 Mounts
# or, with compose, open docker-compose.yml and read the 'volumes:' lines
```
If you see something like `/srv/web:/app`, the real code is in `/srv/web` on the
host. You edit it there directly.

**Case B - code is baked into the image (no mount).** You either edit inside the
container, or edit the source + rebuild. Editing inside is faster mid-game.

## 3. Back up FIRST
```bash
./backup.sh /srv/web                      # the mounted source dir
# plus any data volume the challenge uses:
./backup.sh /srv/web mysql_data
# full safety net: snapshot the whole container as an image
docker commit <container> backup:web-$(date +%H%M)
```

## 4. Make the smallest fix
- **Case A (mounted):** edit the file on the host with `nano`/`vim`, save.
- **Case B (baked in):**
  ```bash
  docker exec -it <container> sh      # get a shell inside
  # edit the file (vi), then exit
  ```
  or edit the host source and rebuild: `docker compose build <svc>`.

## 5. Restart the service (NOT the whole box)
```bash
docker compose restart <svc>     # compose
# or
docker restart <container>       # single container
```
Restart only what you patched. Restarting everything risks extra downtime.

## 6. VERIFY it's still up -- the step that saves your SLA
```bash
curl -s http://localhost:<port>/health     # or the normal user flow
```
- Normal request still works + your exploit now fails  => keep it.
- Anything broke  => revert immediately:
  ```bash
  # mounted source:
  rm -rf /srv/web && cp -r ~/backups/web.ORIGINAL /srv/web
  docker compose restart <svc>
  # or roll back to the committed image if you rebuilt
  ```

## Gotchas
- **Don't `docker compose down`** mid-game unless you must -- it stops everything
  and you bleed SLA until it's back. Prefer `restart`.
- **Don't delete volumes** (`docker volume rm`, `down -v`) -- that can wipe the
  data the checker relies on, instant DOWN.
- **Logs for spotting attacks:** `docker logs -f <container>` alongside your
  `tcpdump`. Repeated weird requests = someone's exploit; read it, patch it, steal it.
- **Resources are tight (~7.7 GB RAM).** Don't run Ghidra + a Dockerized traffic
  analyzer + a browser all at once; you'll OOM. Keep it lean.
