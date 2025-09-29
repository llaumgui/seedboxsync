---
title: Frontend
summary: SeedboxSyncFront  — The seedboxsync frontend
hide:
  - navigation
---
---

:information_source: **SeedboxSync aims to be as simple as possible!**
That’s why it was originally designed as a pure command-line utility.

However, a dedicated **frontend** is also available to help you monitor and visualize what SeedboxSync is doing.
This frontend is provided as a [separate GitHub project](https://github.com/llaumgui/seedboxsync-front) and leverages SeedboxSync’s database to extract information and generate useful statistics.

---

## Installation

### Using docker

> :information_source: **Recommended:** Docker is the preferred installation method for stability and isolation.

You must [install SeedboxSync first](getting-started/docker.md) and use **docker-compose**:

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

  seedboxsync-front:
    container_name: seedboxsync-front
    hostname: seedboxsync-front
    image: ghcr.io/llaumgui/seedboxsync-front:latest
    restart: unless-stopped
    environment:
      TZ: 'Europe/Paris'
      PUID: 1000
      PGID: 100
      FLASK_SECRET_KEY: MySecretKey
    volumes:
      - /data/seedboxsync/config:/config
      - /data/seedboxsync/downloads:/downloads
    ports:
      - 8000:8000
```

Once installed, you can access the frontend: [http://127.0.0.1:8000](http://127.0.0.1:8000/).

#### Docker tags

| Tags         | Description                                     | Stable |
| ------------ | ----------------------------------------------- | ------ |
| `latest`     | Based on the latest release version             | ✅     |
| `main`       | Built from the `main` branch (development)      | ❌     |

#### Environment Variables

| Variable           | Description                                   | Default Value |
|--------------------|-----------------------------------------------|---------------|
| `TZ`               | Timezone configuration                        |               |
| `PUID`             | User ID for the main process                  | `1000`        |
| `PGID`             | Group ID for the main process                 | `1000`        |
| `FLASK_SECRET_KEY` | The [Flask's secret](https://flask.palletsprojects.com/en/stable/config/#SECRET_KEY) key that will be used for securely signing the session cookie and can be used for any other security related needs by extensions or your application. It should be a long random bytes or str. | `dev` |
| `GUNICORN_WORKERS` | The number of [Gunicorn worker](https://docs.gunicorn.org/en/stable/run.html#commonly-used-arguments) processes. This number should generally be between 2-4 workers per core in the server. | `1` |
| `GUNICORN_BIND`    | Specify a server socket to bind. Server sockets can be any of $(HOST), $(HOST):$(PORT), fd://$(FD), or unix:$(PATH). An IP is a valid $(HOST). | `0.0.0.0:8000` |

### Using pip

SeedboxSyncFront is [available on PyPI](https://pypi.org/project/seedboxsync-front/).

> :warning: **Warning:** Docker is the recommended method.

```bash
pip install seedboxsync-front
flask flask --app seedboxsync_front.app:main run
```

Once installed, you can access the frontend: [http://127.0.0.1:5000](http://127.0.0.1:5000/).
