---
title: Upgrade from v3 to v4
summary: Upgrade guide for Seedboxsync from v3 to v4
---

Seedboxsync v4 introduces a merge between the backend and frontend into a single application. As a result, running `seedboxsync-front` as a separate container is no longer required.

## Update Docker Compose

After merge compose (don't forget `FLASK_SECRET_KEY`), you can safely remove the `seedboxsync-front` service from your `docker-compose.yml` file and keep only the main application service.

## Reverse Proxy Setup (Traefik, Nginx, etc.)

If you are using a reverse proxy such as Traefik, update your routing rules so that incoming traffic points directly to the main `seedboxsync` application container.

> **Note:** The default port remains unchanged (**8000**).

## Configuration Migration

Starting with v4, application configuration is managed directly in the database rather than through a configuration file:

1. Retrieve your current settings from your existing `seedboxsync.yml` file.
2. Open the Seedboxsync web interface.
3. Enter your settings into the configuration form in the frontend to complete the setup.
