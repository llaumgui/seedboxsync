---
title: Usage
summary: SeedboxSync usage
---

## Use in command line

```bash
usage: seedboxsync [-h] [-d] [-q] [-v] {sync,list,clean} ...

Script for sync operations between your NAS and your seedbox

options:
  -h, --help         show this help message and exit
  -d, --debug        full application debug mode
  -q, --quiet        suppress all console output
  -v, --version      show program's version number and exit

sub-commands:
  {sync,list,clean}
    sync             all synchronization operations
    list             all list operations
    clean            all cleaning operations

Usage: seedboxsync sync blackhole --dry-run
```

* Sync blackhole:

```bash
seedboxsync sync blackhole
```

* Sync seedbox:

```bash
seedboxsync sync seedbox
```

* List 20 last torrents downloaded from seedbox:

```bash
seedboxsync search downloaded -n 20
```

* List 20 last torrents uploaded to seedbox:

```bash
seedboxsync search uploaded -n 20
```

* List download in progress:

```bash
seedboxsync search progress
```

* Clean all download in progress:

```bash
seedboxsync clean progress
```

* Remove downloaded torrent with id 123 (to enable re-download):

```bash
seedboxsync clean downloaded 123
```

* Get statistics by month:

```bash
seedboxsync stats by-month
```

* Get statistics by year:

```bash
seedboxsync stats by-year
```

## Use in crontab

> :warning: **Warning:** Docker is the recommended method and have a cron feature out-of-the-box.

```bash
# Sync blackhole every 2mn
*/2 * * * * root seedboxsync -q sync blackhole --ping

# Download torrents finished every 15mn
*/15 * * * * root seedboxsync -q sync seedbox --ping
```
