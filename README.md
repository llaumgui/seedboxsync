# SeedboxSync
[![Build Status](https://travis-ci.org/llaumgui/seedboxsync.svg?branch=master)](https://travis-ci.org/llaumgui/seedboxsync) [![Code Climate](https://codeclimate.com/github/llaumgui/seedboxsync/badges/gpa.svg)](https://codeclimate.com/github/llaumgui/seedboxsync) [![PyPI version](https://badge.fury.io/py/seedboxsync.svg)](https://pypi.python.org/pypi/seedboxsync)

Provides synchronization functions between your NAS and your seedbox:
* Syncs a local black hole (ie: a NAS folder) with the black hole of your seedbox.
```bash
seedboxsync --blackhole
```
* Downloads files from your seedbox to your NAS. Stores the list of downloaded files in a sqlite database, to prevent to download a second time.
```bash
seedboxsync --download
```
* Also provides queries to know last torrents, last downloads, etc.

__Currently, only sFTP is supported__.


## Requirements
See requirements.txt.


## Installation

### With pip
In root:
```bash
pip install seedboxsync
```
Or in user:
```bash
pip install --user seedboxsync
```

### Clone repository
* Install script in /opt/llaumgui/seedboxsync:

```bash
sudo mkdir -p /opt/llaumgui
cd /opt/llaumgui
sudo git clone https://github.com/llaumgui/seedboxsync.git
cd seedboxsync
sudo chmod +x seedboxsync.py
```


## Configuration
You can use the example configuration, this file is located in:
* /usr/local/etc/ (pip install)
* ~/.local/etc/ (pip install in user mode)
* /opt/llaumgui/seedboxsync (clone repository)

```bash
sudo cp /usr/local/etc/seedbox.ini.dist /etc/seedbox.ini
```

You can put your configuration in:
* seedboxsync.ini in the root of the sources folder.
* ~/.seedboxsync/seedboxsync.ini
* /usr/local/etc/seedboxsync.ini
* /usr/local/etc/seedboxsync/seedboxsync.ini
* /etc/seedboxsync.ini
* /etc/seedboxsync/seedboxsync.ini


## Usage

### In command line
```bash
usage: seedboxsync.py [-h] [--blackhole | --lasts-torrents [LASTS_TORRENTS] |
                      --download | --lasts-downloads [LASTS_DOWNLOADS] |
                      --unfinished-downloads] [-q]

Script for sync operations between your NAS and your seedbox.

optional arguments:
  -h, --help            show this help message and exit
  --blackhole           send torrent from the local blackhole to the seedbox
                        blackhole
  --lasts-torrents [LASTS_TORRENTS]
                        get list of lasts torrents uploaded
  --download            download finished files from seedbox to NAS
  --lasts-downloads [LASTS_DOWNLOADS]
                        get list of lasts downloads
  --unfinished-downloads
                        get list of unfinished downloads
  -q, --quiet
```

### In crontab

```bash
# Sync blackhole every 2mn
*/2 * * * * root seedboxsync --blackhole

# Download torrents finished every 15mn
*/15 * * * * root seedboxsync.py --download
```


## License
Released under the [GPL v2](http://opensource.org/licenses/GPL-2.0).