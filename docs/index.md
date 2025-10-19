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

**SeedboxSync** provides a seamless and automated way to synchronize, download, and manage your torrents between your NAS and seedbox.

## Key Features

* **🔄 Two-way synchronization**:
    * Sync from NAS to Seedbox (upload blackhole folder)
    * Sync from Seedbox to NAS (automatic download with de-duplication tracking)
* **📥 Download management**: Prevent duplicate transfers using an integrated SQLite database
* **📊 Statistics and reporting**: View monthly and yearly download statistics
* **✅ Quality and testing**: Over 80% unit test coverage
* **🌐 Web frontend**: A web front-end is also available as a separate project if you don't want to use the CLI for management and reporting.

<p style="text-align:center; margin-top: 60px">
  <a href="https://www.python.org"><img alt="Python logo" src="images/python-powered-w-140x56.png" /></a> <a href="https://builtoncement.com"><img alt="SeedboxSync logo" src="images/logo-cement.png" /></a> <a href="https://docs.peewee-orm.com"><img alt="peewee logo" src="images/logo-peewee.png" /></a>
</p>
