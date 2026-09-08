---
title: Upgrade from v4 to v4.x
summary: Upgrade guide for Seedboxsync from v4 to v4.x
---

## Before upgrading

Database migrations are applied automatically when the new SeedboxSync version starts. A migrated database may not be compatible with an older release.

Always stop SeedboxSync and create a backup before upgrading. Stopping the container first ensures that the SQLite database and its associated files are in a consistent state.

The following example assumes that `/data/seedboxsync/config` is mounted as `/config`:

```bash
docker compose stop seedboxsync
mkdir -p /data/seedboxsync/backups
cp -a /data/seedboxsync/config \
  "/data/seedboxsync/backups/config-$(date +%Y%m%d-%H%M%S)"
```

Keep the backup until the upgraded installation has been fully validated.

## Upgrade from v4.0 to v4.1

SeedboxSync v4.1 introduces a built-in authentication mechanism.

Upgrade and restart the container:

```bash
docker compose pull seedboxsync
docker compose up -d seedboxsync
docker compose logs --tail 100 seedboxsync
```

Once upgraded, log in for the first time using the initial credentials:

* **Username:** `admin`
* **Password:** `seedboxsync`

> :warning: **Security notice:** Change the initial administrator password immediately under **Settings > Users** before exposing the application to other users or to the Internet.

After logging in, you can disable built-in authentication if authentication is delegated to a reverse proxy or an OIDC provider. Validate the alternative authentication method before disabling built-in authentication.
