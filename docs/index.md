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

**SeedboxSync** is designed for users who run a NAS (Synology, TrueNAS, Unraid, Linux...) alongside a remote seedbox and want to automate torrent transfers without manual intervention.

**SeedboxSync** automates the complete lifecycle of your torrents between your NAS and your seedbox: upload `.torrent` files, download completed data, avoid duplicate transfers, and monitor everything from a web interface.

## Features

* **🔄 Torrent workflow automation**
    * Upload `.torrent` files from your NAS to your seedbox (blackhole directory).
    * Automatically download completed torrents back to your NAS.
* **📥 Smart download tracking**: Prevent duplicate transfers and keep track of downloaded torrents using an embedded SQLite database.
* **🌐 Web frontend**: Monitor your downloads and syncs in real-time through a user-friendly web interface.
* **📊 Statistics and reporting**: View monthly and yearly download statistics
* **🗄️ REST API**: Integrate SeedboxSync with your own tools and automation workflows.

## Build with

<p style="text-align:center;">
  <a href="https://www.python.org"><img alt="Python logo" src="./images/python-powered-w-140x56.png" /></a> <a href="https://flask.palletsprojects.com"><img alt="Flask logo" src="./images/logo-flask.png" /></a> <a href="https://docs.peewee-orm.com"><img alt="peewee logo" src="./images/logo-peewee.png" /></a>
</p>
