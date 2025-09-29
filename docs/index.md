---
title: SeedboxSync documentation
description: Script for synchronizing operations between your NAS and your seedbox.
hide:
  - navigation
  - toc
---

<p align="center">
  <img alt="SeedboxSync logo" src="images/seedboxsync.png" />
</p>

**SeedboxSync** provides powerful synchronization features between your NAS and your seedbox, making torrent management seamless and automated.

Key Features:

- **Local to Seedbox Sync**: Synchronize a local blackhole folder (e.g., on your NAS) with the blackhole directory on your seedbox.
- **Seedbox to NAS Downloads**: Automatically download files from your seedbox to your NAS, keeping track of downloaded files in a SQLite database to prevent duplicates.
- **Query & Reporting**: Retrieve information such as recent torrents, latest downloads, and other useful statistics.
