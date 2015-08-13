# SeedboxSync
[![Build Status](https://travis-ci.org/llaumgui/seedboxsync.svg?branch=master)](https://travis-ci.org/llaumgui/seedboxsync) [![Code Climate](https://codeclimate.com/github/llaumgui/seedboxsync/badges/gpa.svg)](https://codeclimate.com/github/llaumgui/seedboxsync) [![Test Coverage](https://codeclimate.com/github/llaumgui/seedboxsync/badges/coverage.svg)](https://codeclimate.com/github/llaumgui/seedboxsync/coverage) [![GitHub version](https://badge.fury.io/gh/llaumgui%2Fseedboxsync.svg)](https://github.com/llaumgui/seedboxsync/)

Provides synchronization functions between your NAS and your seedbox:
* Sync a local black hole (ie: NAS folder) with the black hole of your seedbox.
* Download files from your Seedbox to your NAS. Store in a sqlite database the list of downloaded files to prevent download a second time.

__Currently, only sFTP is supported__.


## Requirements
See requirements.txt.


## Installation

### With pip
Not implemented yet...

### Clone repository
* Install script in /opt/llaumgui/seedboxsync:

```bash
sudo mkdir -p /opt/llaumgui
cd /opt/llaumgui
sudo git clone https://github.com/llaumgui/seedboxsync.git
cd seedboxsync
sudo chmod +x get_finished.py  blackhole.py
```

* Use default configuration:

```bash
sudo cp seedbox.ini.dist seedbox.ini
```

* Edit seedbox.ini and add your parameters.


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
*/2 * * * * root <PATH_OF_SEEDBOXSYNC>/seedboxsync.py --blackhole

# Download torrents finished every 15mn
*/15 * * * * root <PATH_OF_SEEDBOXSYNC>/seedboxsync.py --download
```


## License
Released under the [GPL v2](http://opensource.org/licenses/GPL-2.0).