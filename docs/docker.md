---
layout: page
title: Docker
description: How to install SeedboxSync with Docker
order: 1
---

* Setup your `configuration.yml` (see [configuration](https://llaumgui.github.io/seedboxsync/configuration.html)).
* Run `docker` and mount your configuration.yml.

```bash
docker run -d \
  --volumes /data/seedboxsync/seedboxsync.yml:/config/seedboxsync.yml \
  ghcr.io/llaumgui/seedboxsync:latest
```

With docker-compose:

```bash
  seedboxsync:
    container_name: seedboxsync
    image: ghcr.io/llaumgui/seedboxsync:latest
    restart: always
    environment:
      TZ: 'Europe/Paris'
    volumes:
     - /data/seedboxsync/seedboxsync.yml:/config/seedboxsync.yml
     - /data/seedboxsync/watch:/watch
     - /data/seedboxsync/download:/download
```
