---
title: Frontend
summary: SeedboxSyncFront  — The seedboxsync frontend
hide:
  - navigation
---

:information_source: **SeedboxSync aims to be as simple as possible!**
That’s why it was originally designed as a pure command-line utility.

However, a dedicated **frontend** is also available to help you monitor and visualize what SeedboxSync is doing.
This frontend is provided as a [separate GitHub project](https://github.com/llaumgui/seedboxsync-front) and leverages SeedboxSync’s database to extract information and generate useful statistics.

:warning: Currently, the front-end does not implement any authentication method.
You are responsible for handling authentication through a reverse proxy or another solution.

Key Features:

* **🌐 Dashboard interface**: Monitor your downloads and syncs in real-time through a user-friendly web interface.
* **📊 Visual statistics**: Access detailed reports of your downloads, including monthly and yearly statistics.
* **🛠️ Manage downloads**: Remove downloads directly from the dashboard to allow re-downloading.
* **🔄 Two-way sync overview**: Quickly see the status of NAS-to-Seedbox and Seedbox-to-NAS synchronization.
* **⚡ Auto-refresh**: Automatically refresh data to keep your dashboard up-to-date without manual reloads.
* **🗄️ API access**: Interact programmatically with your downloads and syncs using a REST API.

---

<div align="center">
    <table>
    <tr>
        <td align="center">
            <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync-front/refs/heads/main/screenshots/homepage.png">
                <img alt="Main page" src="https://raw.githubusercontent.com/llaumgui/seedboxsync-front/refs/heads/main/screenshots/homepage.png" width="300"/>
            </a>
            <br><em>Main page</em>
        </td>
        <td align="center">
            <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync-front/refs/heads/main/screenshots/downloaded.png">
                <img alt="Downloaded files" src="https://raw.githubusercontent.com/llaumgui/seedboxsync-front/refs/heads/main/screenshots/downloaded.png" width="300"/>
            </a>
            <br><em>Downloaded files</em>
        </td>
    </tr>
    <tr>
        <td align="center">
            <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync-front/refs/heads/main/screenshots/uploaded.png">
                <img alt="Uploaded torrents" src="https://raw.githubusercontent.com/llaumgui/seedboxsync-front/refs/heads/main/screenshots/uploaded.png" width="300"/>
            </a>
            <br><em>Uploaded torrents</em>
        </td>
            <td align="center">
            <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync-front/refs/heads/main/screenshots/info.png">
              <img alt="Informations" src="https://raw.githubusercontent.com/llaumgui/seedboxsync-front/refs/heads/main/screenshots/info.png" width="300"/>
            </a>
            <br><em>info</em>
        </td>
    </tr>
    <tr>
        <td align="center">
            <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync-front/refs/heads/main/screenshots/stats.png">
                <img alt="Statistics" src="https://raw.githubusercontent.com/llaumgui/seedboxsync-front/refs/heads/main/screenshots/stats.png" width="300"/>
            </a>
            <br><em>Statistics</em>
        </td>
        <td align="center">
            <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync-front/refs/heads/main/screenshots/api-spec.png">
                <img alt="API SPEC" src="https://raw.githubusercontent.com/llaumgui/seedboxsync-front/refs/heads/main/screenshots/api-spec.png" width="300"/>
            </a>
            <br><em>API   </em>
        </td>
    </tr>
    </table>
</div>

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
| `GUNICORN_BIND`    | Specify a server socket to bind. Server sockets can be any of `$(HOST)`, `$(HOST):$(PORT)`, `fd://$(FD)`, or `unix:$(PATH)`. An IP is a valid `$(HOST)`. | `0.0.0.0:8000` |

### Using pip

SeedboxSyncFront is [available on PyPI](https://pypi.org/project/seedboxsync-front/).

> :warning: **Warning:** Docker is the recommended method.

```bash
pip install seedboxsync-front
flask flask --app seedboxsync_front.app:main run
```

Once installed, you can access the frontend: [http://127.0.0.1:5000](http://127.0.0.1:5000/).
