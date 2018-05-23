# SeedboxSync

[![Build Status](https://travis-ci.org/llaumgui/seedboxsync.svg?branch=master)](https://travis-ci.org/llaumgui/seedboxsync)
[![Code Climate](https://codeclimate.com/github/llaumgui/seedboxsync/badges/gpa.svg)](https://codeclimate.com/github/llaumgui/seedboxsync)
[![PyPI version](https://badge.fury.io/py/seedboxsync.svg)](https://pypi.python.org/pypi/seedboxsync)
[![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/llaumgui/seedboxsync.svg)](http://isitmaintained.com/project/llaumgui/seedboxsync "Average time to resolve an issue")
[![Percentage of issues still open](http://isitmaintained.com/badge/open/llaumgui/seedboxsync.svg)](http://isitmaintained.com/project/llaumgui/seedboxsync "Percentage of issues still open")

Provides synchronization functions between your NAS and your seedbox:

* Syncs a local black hole (ie: a NAS folder) with the black hole of your seedbox.
* Downloads files from your seedbox to your NAS. Stores the list of downloaded files in a sqlite database, to prevent to download a second time.
* Also provides queries to know last torrents, last downloads, etc.

## Python support

* Python 3.4+ support look at [_master_](https://github.com/llaumgui/seedboxsync/tree/master) branch.
* Legacy Python 2.7 support look at the [_legacy-python2_](https://github.com/llaumgui/seedboxsync/tree/legacy-python2) branch.

## Full documentation

See: [https://llaumgui.github.io/seedboxsync/](https://llaumgui.github.io/seedboxsync/)

## License

Released under the [GPL v2](http://opensource.org/licenses/GPL-2.0).