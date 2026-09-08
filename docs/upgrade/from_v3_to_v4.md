---
title: Upgrade from v3 to v4
summary: Upgrade guide for Seedboxsync from v3 to v4
---

Seedboxsync v4 introduces a merge between the backend and frontend into a single application. As a result, running `seedboxsync-front` as a separate container is no longer required.

## Before upgrading

Before changing the Docker Compose configuration:

1. Stop the v3 containers.
2. Back up the complete v3 configuration directory.
3. Back up `seedboxsync.yml` and the current Docker Compose file.
4. Record the image tags currently in use.

Keep the `seedboxsync-front` service definition and its previous image tag until the v4 installation has been validated. It can be removed permanently after the migration succeeds.

## Update Docker Compose

Merge the backend and frontend configuration into the main `seedboxsync` service and configure `FLASK_SECRET_KEY`. See the [Docker installation guide](../getting-started/docker.md) for a current Compose example and secret-generation instructions.

Do not permanently remove the old `seedboxsync-front` service or its configuration until the v4 installation has been validated.

## Reverse Proxy Setup (Traefik, Nginx, etc.)

If you are using a reverse proxy such as Traefik, update your routing rules so that incoming traffic points directly to the main `seedboxsync` application container.

> **Note:** The default port remains unchanged (**8000**).

## Configuration Migration

Starting with v4, application configuration is managed directly in the database rather than through a configuration file. Settings from the v3 `seedboxsync.yml` file are not imported automatically.

After starting v4:

1. Sign in to the Web UI.
2. Re-enter the values from `seedboxsync.yml`.
3. Leave synchronization tasks disabled until every local and remote path has been reviewed.
4. Enable and validate each synchronization task separately.
5. Keep the v3 configuration backup until both upload and download workflows have been verified.
