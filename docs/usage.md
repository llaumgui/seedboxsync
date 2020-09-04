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
usage: seedboxsync [-h] [-d] [-q] [-v]
                   {clean-in-progress,list-downloaded,ld,list-in-progress,lip,list-uploaded,lu,sync-blackhole,sb,sync-seedbox,ss}
                   ...

Script for sync operations between your NAS and your seedbox

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           full application debug mode
  -q, --quiet           suppress all console output
  -v, --version         show program's version number and exit

sub-commands:
  {clean-in-progress,list-downloaded,ld,list-in-progress,lip,list-uploaded,lu,sync-blackhole,sb,sync-seedbox,ss}
    clean-in-progress   clean the list of files currently in download from
                        seedbox
    list-downloaded (ld)
                        list of lasts files downloaded from seedbox
    list-in-progress (lip)
                        list of files currently in download from seedbox
    list-uploaded (lu)  list of lasts torrents uploaded from blackhole
    sync-blackhole (sb)
                        sync torrent from blackhole to seedbox
    sync-seedbox (ss)   sync file from seedbox

Usage: seedboxsync sync-blackhole --dry-run
```

## Use in crontab

```bash
# Sync blackhole every 2mn
*/2 * * * * root seedboxsync -q sync-blackhole --ping

# Download torrents finished every 15mn
*/15 * * * * root seedboxsync -q sync-seedbox --ping
```
