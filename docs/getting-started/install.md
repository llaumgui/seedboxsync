---
title: Installation
summary: Installing SeedboxSync
---

## Using docker

> :information_source: **Recommended:** Docker is the preferred installation method for stability and isolation.

See [documentation](docker.md).

## Using pip

SeedboxSync is [available on PyPI](https://pypi.org/project/seedboxsync/).

> :warning: **Warning:** Docker is the recommended method.

* Install:

```bash
pip install seedboxsync
```

* Running WebUI:

```bash
flask --app seedboxsync.app:app run
```

* Running task manager:

```bash
huey_consumer seedboxsync.taskmanager.huey -w 2 -k thread
```

> :warning: **Security notice:** SeedboxSync creates an initial administrator account with the username `admin` and password `seedboxsync`. Change this password immediately under **Settings > Users** before exposing the application to other users or to the Internet.

Once installed, you can access the frontend: [http://127.0.0.1:5000](http://127.0.0.1:5000/).
