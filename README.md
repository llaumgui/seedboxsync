# SeedboxSync
[![Build Status](https://travis-ci.org/llaumgui/seedboxsync.svg?branch=master)](https://travis-ci.org/llaumgui/seedboxsync) [![Code Climate](https://codeclimate.com/github/llaumgui/seedboxsync/badges/gpa.svg)](https://codeclimate.com/github/llaumgui/seedboxsync) [![PyPI version](https://badge.fury.io/py/seedboxsync.svg)](https://pypi.python.org/pypi/seedboxsync)

Provides synchronization functions between your NAS and your seedbox:
* Syncs a local black hole (ie: a NAS folder) with the black hole of your seedbox.
* Downloads files from your seedbox to your NAS. Stores the list of downloaded files in a sqlite database, to prevent to download a second time.
* Also provides queries to know last torrents, last downloads, etc.

__Currently, only sFTP is supported__.


## Requirements
See requirements.txt.


## Documentation
See: [https://llaumgui.github.io/seedboxsync/](https://llaumgui.github.io/seedboxsync/)


## License
Released under the [GPL v2](http://opensource.org/licenses/GPL-2.0).