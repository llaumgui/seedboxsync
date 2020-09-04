---
layout: full
homepage: true
disable_anchors: true
description: Script for sync operations between your NAS and your seedbox.
---

# SeedboxSync's documentation

![SeedboxSync's logo](images/seedboxsync.png)

Provides synchronization functions between your NAS and your seedbox:

* Syncs a local blackhole (ie: a NAS folder) with the blackhole of your seedbox.
* Downloads files from your seedbox to your NAS. Stores the list of downloaded files in a sqlite database, to prevent to download a second time.
* Also provides queries to know last torrents, last downloads, etc.
