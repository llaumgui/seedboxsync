---
layout: page
title: Usage
description: SeedboxSync usage
order: 3
---

## Launch SeedboxSync

```bash
seedboxsync
```

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

## Use in crontab

```bash
# Sync blackhole every 2mn
*/2 * * * * root seedboxsync -q sync blackhole --ping

# Download torrents finished every 15mn
*/15 * * * * root seedboxsync -q sync seedbox --ping
```
