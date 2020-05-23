# SeedboxSync

[![Python CI/CD](https://github.com/llaumgui/seedboxsync/workflows/Python%20CI/CD/badge.svg)](https://github.com/llaumgui/seedboxsync/actions?query=workflow%3A%22Python+CI%2FCD%22) [![SonarCloud: Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=llaumgui:seedboxsync&metric=alert_status)](https://sonarcloud.io/dashboard?id=llaumgui:seedboxsync)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=llaumgui%3Aseedboxsync&metric=coverage)](https://sonarcloud.io/dashboard?id=llaumgui%3Aseedboxsync)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=llaumgui%3Aseedboxsync&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=llaumgui%3Aseedboxsync) [![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=llaumgui%3Aseedboxsync&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=llaumgui%3Aseedboxsync) [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=llaumgui%3Aseedboxsync&metric=security_rating)](https://sonarcloud.io/dashboard?id=llaumgui%3Aseedboxsync)<br />
[![GitHub license](https://img.shields.io/github/license/llaumgui/seedboxsync.svg)](https://github.com/llaumgui/seedboxsync/blob/master/LICENSE)
[![PyPI version](https://badge.fury.io/py/seedboxsync.svg)](https://pypi.python.org/pypi/seedboxsync)<br />
[![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/llaumgui/seedboxsync.svg)](http://isitmaintained.com/project/llaumgui/seedboxsync "Average time to resolve an issue")
[![Percentage of issues still open](http://isitmaintained.com/badge/open/llaumgui/seedboxsync.svg)](http://isitmaintained.com/project/llaumgui/seedboxsync "Percentage of issues still open")

Provides synchronization functions between your NAS and your seedbox:

* Syncs a local black hole (ie: a NAS folder) with the black hole of your seedbox.
* Downloads files from your seedbox to your NAS. Stores the list of downloaded files in a sqlite database, to prevent to download a second time.
* Also provides queries to know last torrents, last downloads, etc.

## Full documentation

See: [https://llaumgui.github.io/seedboxsync/](https://llaumgui.github.io/seedboxsync/)

## License

Released under the [GPL v2](http://opensource.org/licenses/GPL-2.0).
