# SeedboxSync

[![Author][ico-twitter]][link-twitter]
[![Build Status][ico-ghactions]][link-ghactions]
[![Latest Version][ico-version]][link-pypi]
[![Libraries.io dependency status for latest release][ico-dependencies]](requirements.txt)
[![Software License][ico-license]](LICENSE)

[![Quality Gate Status][ico-sonarcloud-gate]][link-sonarcloud-gate]
[![Coverage][ico-sonarcloud-coverage]][link-sonarcloud-coverage]
[![Maintainability Rating][ico-sonarcloud-maintainability]][link-sonarcloud-maintainability]
[![Reliability Rating][ico-sonarcloud-reliability]][link-sonarcloud-reliability]
[![Security Rating][ico-sonarcloud-security]][link-sonarcloud-security]

Provides synchronization functions between your NAS and your seedbox:

* Syncs a local black hole (ie: a NAS folder) with the black hole of your seedbox.
* Downloads files from your seedbox to your NAS. Stores the list of downloaded files in a sqlite database, to prevent to download a second time.
* Also provides queries to know last torrents, last downloads, etc.

## Full documentation

See: [https://llaumgui.github.io/seedboxsync/](https://llaumgui.github.io/seedboxsync/)

## License

Released under the [GPL v2](http://opensource.org/licenses/GPL-2.0).

[ico-twitter]: https://img.shields.io/static/v1?label=Author&message=llaumgui&color=000&logo=x&style=flat-square
[link-twitter]: https://twitter.com/llaumgui
[ico-ghactions]: https://img.shields.io/github/actions/workflow/status/llaumgui/seedboxsync/devops.yml?branch=main&style=flat-square&logo=github&label=DevOps
[link-ghactions]: https://github.com/llaumgui/seedboxsync/actions
[ico-version]: https://img.shields.io/pypi/v/seedboxsync?include_prereleases&label=Package%20version&style=flat-square&logo=python
[link-pypi]:https://pypi.org/project/seedboxsync/
[ico-license]: https://img.shields.io/github/license/llaumgui/seedboxsync?style=flat-square
[ico-sonarcloud-gate]: https://sonarcloud.io/api/project_badges/measure?branch=main&project=llaumgui_seedboxsync&metric=alert_status
[link-sonarcloud-gate]: https://sonarcloud.io/dashboard?id=llaumgui_seedboxsync&branch=main
[ico-sonarcloud-coverage]: https://sonarcloud.io/api/project_badges/measure?project=llaumgui_seedboxsync&metric=coverage
[link-sonarcloud-coverage]: https://sonarcloud.io/dashboard?id=llaumgui_seedboxsync
[ico-sonarcloud-maintainability]: https://sonarcloud.io/api/project_badges/measure?project=llaumgui_seedboxsync&metric=sqale_rating
[link-sonarcloud-maintainability]: https://sonarcloud.io/dashboard?id=llaumgui_seedboxsync
[ico-sonarcloud-reliability]: https://sonarcloud.io/api/project_badges/measure?project=llaumgui_seedboxsync&metric=reliability_rating
[link-sonarcloud-reliability]: https://sonarcloud.io/dashboard?id=llaumgui_seedboxsync
[ico-sonarcloud-security]: https://sonarcloud.io/api/project_badges/measure?project=llaumgui_seedboxsync&metric=security_rating
[link-sonarcloud-security]: https://sonarcloud.io/dashboard?id=llaumgui_seedboxsync
[ico-dependencies]: https://img.shields.io/librariesio/release/pypi/seedboxsync?style=flat-square
