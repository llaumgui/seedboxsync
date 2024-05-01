---
layout: page
title: Docker
description: How to install SeedboxSync with Docker
order: 1
---

## Pull image

From Docker Hub:

```bash
docker pull llaumgui/seedboxsync
```

Or from GitHub Packages:

```bash
docker pull ghcr.io/llaumgui/seedboxsync
```

## Use image

* Setup your `configuration.yml` (see [configuration](https://llaumgui.github.io/seedboxsync/configuration.html)).
* Run `docker` and mount your configuration.yml and others path

```bash
docker run --rm \
  --volume /data/seedboxsync/config:/config/seedboxsync.yml \
  --volume /data/seedboxsync/watch:/watch \
  --volume /data/seedboxsync/download:/download \
  ghcr.io/llaumgui/seedboxsync:latest --help
```

* Use a script to shortcut the call:

```bash
#!/bin/bash

CONTAINER_NAME="ghcr.io/llaumgui/seedboxsync:latest"
COMMAND="$@"

docker run --rm \
  --volume /data/seedboxsync:/config \
  --volume /data/seedboxsync/watch:/watch \
  --volume /data/seedboxsync/download:/download \
  ${CONTAINER_NAME} ${COMMAND}
```
