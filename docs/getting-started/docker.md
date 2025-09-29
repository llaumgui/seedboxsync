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
    volumes:
      - /data/seedboxsync/config:/config
      - /data/seedboxsync/watch:/watch
      - /data/seedboxsync/downloads:/downloads
```

### Docker tags

| Tags         | Description                                     | Stable |
| ------------ | ----------------------------------------------- | ------ |
| `latest`     | Based on the latest release version             | ✅     |
| `main`       | Built from the `main` branch (development)      | ❌     |

## Extra Features

### s6-overlay Integration

This image uses [s6-overlay](https://github.com/just-containers/s6-overlay) for:

* Multi-process container management and customization.
* Support for changing the UID/GID running the main process.

### Cron Jobs

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

| Variable   | Description                                   | Default Value |
|------------|-----------------------------------------------|---------------|
| `TZ`       | Timezone configuration                        |               |
| `PUID`     | User ID for the main process                  | `1000`        |
| `PGID`     | Group ID for the main process                 | `1000`        |

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
