---
order: 3
---

# Usage

## Launch SeedboxSync

* From a pip installation (recommended method):

```bash
seedboxsync
```

* From a git clone installation:

```bash
cd /path/to/clone && seedboxsync.py
```

## Use in command line

```bash
usage: seedboxsync [-h] [--blackhole | -t [LASTS_TORRENTS] | --download | -d
                   [LASTS_DOWNLOADS] | -u] [-q]

Script for sync operations between your NAS and your seedbox.

optional arguments:
  -h, --help            show this help message and exit
  --blackhole           send torrent from the local blackhole to the seedbox
                        blackhole
  -t [LASTS_TORRENTS], --lasts-torrents [LASTS_TORRENTS]
                        get list of lasts torrents uploaded
  --download            download finished files from seedbox to NAS
  -d [LASTS_DOWNLOADS], --lasts-downloads [LASTS_DOWNLOADS]
                        get list of lasts downloads
  -u, --unfinished-downloads
                        get list of unfinished downloads
  -q, --quiet
```

## Use in crontab

```bash
# Sync blackhole every 2mn
*/2 * * * * root seedboxsync --blackhole

# Download torrents finished every 15mn
*/15 * * * * root seedboxsync --download
```

You can also add a logrotate configuration in /etc/logrotate.d/seedboxsync:

```bash
/var/log/seedboxsync_*.log {
    weekly
    missingok
    rotate 4
    compress
    notifempty
}
```