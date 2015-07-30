# SeedboxSync
[![Build Status](https://travis-ci.org/llaumgui/seedboxsync.svg?branch=master)](https://travis-ci.org/llaumgui/seedboxsync) [![Code Climate](https://codeclimate.com/github/llaumgui/seedboxsync/badges/gpa.svg)](https://codeclimate.com/github/llaumgui/seedboxsync) [![Test Coverage](https://codeclimate.com/github/llaumgui/seedboxsync/badges/coverage.svg)](https://codeclimate.com/github/llaumgui/seedboxsync/coverage) [![GitHub version](https://badge.fury.io/gh/llaumgui%2Fseedboxsync.svg)](https://github.com/llaumgui/seedboxsync/)

Provides 2 scripts:
* __blackhole.py__: sync a local black hole (ie: NAS folder) with the black hole of your seedbox over sFTP.
* __get_finished.py__: download files from your Seedbox to your NAS using sFTP. Store in a sqlite database the list of downloaded files to prevent download a second time.

## Installation
* Install script in /opt/llaumgui/seedboxsync:
~~~bash
sudo mkdir -p /opt/llaumgui
cd /opt/llaumgui
sudo git clone https://github.com/llaumgui/seedboxsync.git
cd seedboxsync
sudo chmod +x get_finished.py  blackhole.py
~~~
* Use default configuration:
~~~bash
sudo cp seedbox.ini.dist seedbox.ini
~~~
* Edit seedbox.ini and add your parameters.

## Usage
### In command line

### In crontab

## License
Released under the [GPL v2](http://opensource.org/licenses/GPL-2.0).
