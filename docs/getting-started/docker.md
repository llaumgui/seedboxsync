---
title: Docker
summary: How to install SeedboxSync with Docker
---

> :information_source: Docker is the recommended installation method. This image includes [s6-overlay](https://github.com/just-containers/s6-overlay) and provides extra features.

## Installation

### Running with Docker CLI

To run the container using the Docker CLI:

```bash
docker run -d \
  --name seedboxsync \
  --volume /data/seedboxsync/config:/config \
  --volume /data/seedboxsync/watch:/watch \
  --volume /data/seedboxsync/downloads:/downloads \
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
```

Once installed, you can access to the frontend: [http://127.0.0.1:8000](http://127.0.0.1:8000/).

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

| Variable           | Description                                   | Default Value |
|--------------------|-----------------------------------------------|---------------|
| `TZ`               | Timezone configuration                        |               |
| `PUID`             | User ID for the main process                  | `1000`        |
| `PGID`             | Group ID for the main process                 | `1000`        |
| `FLASK_SECRET_KEY` | The [Flask's secret](https://flask.palletsprojects.com/en/stable/config/#SECRET_KEY) key that will be used for securely signing the session cookie and can be used for any other security related needs by extensions or your application. It should be a long random bytes or str. | `dev` |
| `GUNICORN_WORKERS` | The number of [Gunicorn worker](https://docs.gunicorn.org/en/stable/run.html#commonly-used-arguments) processes. This number should generally be between 2-4 workers per core in the server. | `1` |
| `GUNICORN_BIND`    | Specify a server socket to bind. Server sockets can be any of `$(HOST)`, `$(HOST):$(PORT)`, `fd://$(FD)`, or `unix:$(PATH)`. An IP is a valid `$(HOST)`. | `0.0.0.0:8000` |
| `HUEY_WORKERS`     | The number of [Huey](https://huey.readthedocs.io/en/latest/deployment.html) workers. | `2`           |
| `HUEY_WORKER_TYPE` | Worker execution model (thread, greenlet, process). Use process for CPU-intensive workloads, and greenlet for IO-heavy workloads. When in doubt, thread is the safest choice. | `thread`      |

## Using the Command Line from the Docker Host

You can use a script to easily run SeedboxSync commands inside the container:

```bash
#!/bin/bash

CONTAINER_NAME="seedboxsync"
UUID=1000
COMMAND="$@"

docker exec -it -u ${UUID} ${CONTAINER_NAME} seedboxsync ${COMMAND}
```

> **Tip:** Replace `UUID` with the user ID you want to use inside the container.
