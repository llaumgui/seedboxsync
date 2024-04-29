---
layout: page
title: Docker
description: How to install SeedboxSync with Docker
order: 1
---

* Setup your `configuration.yml` (see [configuration](https://llaumgui.github.io/seedboxsync/configuration.html)).
* Run `docker` and mount your configuration.yml.

```bash
docker run --rm \
  --volume /data/seedboxsync/seedboxsync.yml:/config/seedboxsync.yml \
  --volume /data/seedboxsync/watch:/watch \
  --volume /data/seedboxsync/download:/download \
  ghcr.io/llaumgui/seedboxsync:latest --help
```

* Use a script to shortcur the call:

```bash
#!/bin/bash

CONTAINER_NAME="ghcr.io/llaumgui/seedboxsync:latest"
ARGV="$@"

docker run --rm \
  --volume /data/seedboxsync/seedboxsync.yml:/config/seedboxsync.yml \
  --volume /data/seedboxsync/watch:/watch \
  --volume /data/seedboxsync/download:/download \
  ${CONTAINER_NAME} ${COMMAND}
```
