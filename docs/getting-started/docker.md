---
title: Docker
summary: How to install SeedboxSync with Docker
---

> :information_source: Docker is the recommended installation method. This image includes [s6-overlay](https://github.com/just-containers/s6-overlay) and provides extra features.

## Installation

### Generate the Flask secret key

SeedboxSync uses `FLASK_SECRET_KEY` to sign authentication session cookies.
Generate a unique random value before starting the container:

```bash
openssl rand -hex 32
```

Alternatively, using Python:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Running with Docker CLI

To run the container using the Docker CLI:

```bash
docker run -d \
  --name seedboxsync \
  --volume /data/seedboxsync/config:/config \
  --volume /data/seedboxsync/watch:/watch \
  --volume /data/seedboxsync/downloads:/downloads \
  -p 8000:8000 \
  -e TZ=Europe/Paris \
  -e PUID=1000 \
  -e PGID=100 \
  -e FLASK_SECRET_KEY=MySecretKey \
  ghcr.io/llaumgui/seedboxsync:latest
```

### Running with Docker Compose

```yaml
services:
  seedboxsync:
    container_name: seedboxsync
    hostname: seedboxsync
    image: ghcr.io/llaumgui/seedboxsync:latest
    restart: unless-stopped
    environment:
      TZ: 'Europe/Paris'
      PUID: 1000
      PGID: 100
      FLASK_SECRET_KEY: MySecretKey
    volumes:
      - /data/seedboxsync/config:/config
      - /data/seedboxsync/watch:/watch
      - /data/seedboxsync/downloads:/downloads
    ports:
      - "8000:8000"
```

## First-time setup

After starting the container, complete the following steps before enabling automatic synchronization:

> :warning: **Security notice:** SeedboxSync creates an initial administrator account with the username admin` and password `seedboxsync`. Change this password immediately before exposing the application to other users or to the Internet.

1. Open [http://127.0.0.1:8000](http://127.0.0.1:8000/).
2. Sign in using the initial `admin` / `seedboxsync` credentials.
3. Change the default administrator password under
   **Settings > Users**.
4. Open **Settings > Local (NAS)** and configure:
    * `/watch` as the local torrent watch directory.
    * `/downloads` as the local destination directory.
5. Open **Settings > Seedbox** and configure the remote connection, temporary
   directory, torrent watch directory, and completed-download directory.
6. Ensure that the configured remote directories already exist and are
   accessible by the seedbox account.
7. Open **Settings > SeedboxSync** and enable the synchronization tasks you
   want to run.

The Docker task manager checks the local blackhole every minute and the remote seedbox every 15 minutes by default.

### Docker tags

| Tags         | Description                                     | Stable |
| ------------ | ----------------------------------------------- | ------ |
| `latest`     | Based on the latest release version             | ✅     |
| `main`       | Built from the `main` branch                    | 🟡     |
| `develop`    | Built from the `develop` branch (development)   | ❌     |

## Extra Features

### s6-overlay Integration

This image uses [s6-overlay](https://github.com/just-containers/s6-overlay) for:

* Multi-process container management and customization.
* Support for changing the UID/GID running the main process.

### Task manager

* Sync blackhole every minute.
* Sync seedbox every 15 minutes.

## Customization

### Custom UID/GID

You can use `PUID` / `PGID` environment variables to run SeedboxSync as a specific non-root user instead of the default UID 1000.
Just set the environment variables as follows:

```yaml
environment:
  PUID: 1000
  PGID: 100
```

### Environment Variables

| Variable | Description | Default Value |
| --- | --- | --- |
| `TZ` | Timezone configuration | |
| `PUID` | User ID for the main process | `1000` |
| `PGID` | Group ID for the main process | `1000` |
| `FLASK_SECRET_KEY` | The [Flask's secret](https://flask.palletsprojects.com/en/stable/config/#SECRET_KEY) is a random secret used to sign authentication session cookies. It must be generated before the first production start. Changing it invalidates existing sessions. | |
| `GUNICORN_WORKERS` | The number of [Gunicorn worker](https://docs.gunicorn.org/en/stable/run.html#commonly-used-arguments) processes. This number should generally be between 2-4 workers per core in the server. | `1` |
| `GUNICORN_BIND` | Specify a server socket to bind. Server sockets can be any of `$(HOST)`, `$(HOST):$(PORT)`, `fd://$(FD)`, or `unix:$(PATH)`. An IP is a valid `$(HOST)`. | `0.0.0.0:8000` |
| `HUEY_WORKERS` | The number of [Huey](https://huey.readthedocs.io/en/latest/deployment.html) workers. | `2` |
| `HUEY_WORKER_TYPE` | Worker execution model (thread, greenlet, process). Use process for CPU-intensive workloads, and greenlet for IO-heavy workloads. When in doubt, thread is the safest choice. | `thread` |
| `HUEY_LOG_LEVEL` | Logging log level for the task manager. | `INFO` |
| `SYNC_BLACKHOLE_MINUTE` | Huey cron minute configuration. By default every minute. | `*` |
| `SYNC_SEEDBOX_MINUTE` | Huey cron minute configuration. By default every 15 minutes. | `*/15` |

## Using the Command Line from the Docker Host

You can use a script to easily run SeedboxSync commands inside the container:

```bash
#!/bin/bash

CONTAINER_NAME="seedboxsync"
PUID="${PUID:-1000}"

docker exec -it \
  --user "$PUID" \
  "$CONTAINER_NAME" \
  seedboxsync "$@"
```

> **Tip:** `"$@"` preserves every command-line argument exactly, including arguments containing spaces. Override `PUID` or `CONTAINER_NAME` when needed: `PUID=1026 CONTAINER_NAME=seedboxsync ./seedboxsync-docker sync seedbox`.
