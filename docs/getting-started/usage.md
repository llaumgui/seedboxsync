---
title: Usage
summary: SeedboxSync usage
---

## Use in command line

```bash
Usage: seedboxsync [OPTIONS] COMMAND [ARGS]...

  Script for sync operations between your NAS and your seedbox

Options:
  --version             Show the version and exit.
  --debug / --no-debug  Set debug mode.
  -h, --help            Show this message and exit.

Commands:
  clean   Cleaning operations.
  health  Show the health status of the SeedboxSync CLI and web service.
  search  Search operations.
  stats   Stats operations.
  sync    Run synchronization operations.
  task    Task operations on task queue management.
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

## Use with taskmanager

> :warning: **Warning:** Docker is the recommended method and have a task manager feature out-of-the-box.

```bash
huey_consumer seedboxsync.taskmanager.huey -w 2 -k thread
```

or

```bash
just run-taskmanager
```
