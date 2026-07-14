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

```bash
pip install seedboxsync
flask flask --app seedboxsync.app:main run
```

Once installed, you can access the frontend: [http://127.0.0.1:5000](http://127.0.0.1:5000/).
