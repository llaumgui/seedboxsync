---
layout: full
homepage: true
disable_anchors: true
description: Script for synchronizing operations between your NAS and your seedbox.
---

# SeedboxSync Documentation

![SeedboxSync logo](images/seedboxsync.png)

**SeedboxSync** provides powerful synchronization features between your NAS and your seedbox:

* Synchronizes a local blackhole (e.g., a NAS folder) with the blackhole directory on your seedbox.
* Downloads files from your seedbox to your NAS, maintaining a record of downloaded files in a SQLite database to prevent duplicate downloads.
* Offers queries to retrieve information such as recent torrents, latest downloads, and more.
