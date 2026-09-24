# SeedboxSync

[![Author][ico-bluesky]][link-bluesky]
[![Software License][ico-license]](LICENSE)
[![Build Status][ico-ghactions]][link-ghactions]

[![Latest Version][ico-pypi-version]][link-pypi]
[![Docker Pull][ico-docker]][link-docker]
[![Latest Version][ico-version]][link-docker]

[![Quality Gate Status][ico-sonarcloud-gate]][link-sonarcloud-gate]
[![Coverage][ico-sonarcloud-coverage]][link-sonarcloud-coverage]
[![Maintainability Rating][ico-sonarcloud-maintainability]][link-sonarcloud-maintainability]
[![Reliability Rating][ico-sonarcloud-reliability]][link-sonarcloud-reliability]
[![Security Rating][ico-sonarcloud-security]][link-sonarcloud-security]

<p align="center">
  <a href="https://llaumgui.github.io/seedboxsync/" title="Documentation"><img alt="SeedboxSync logo" src="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/logo/128.png" /></a>
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

## Screenshots

<details>
    <summary>All screenshots</summary>
    <div align="center">
        <table>
            <tr>
                <td align="center">
                    <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/login.png"><img alt="Main page" src="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/login.png" width="300"/></a>
                    <br><em>Login page (dark mode)</em>
                </td>
                <td align="center">
                    <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/homepage.png"><img alt="Main page" src="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/homepage.png" width="300"/></a>
                    <br><em>Main page (dark mode)</em>
                </td>
                <td align="center">
                    <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/homepage_light.png"><img alt="Main page" src="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/homepage_light.png" width="300"/></a>
                    <br><em>Main page (light mode)</em>
                </td>
            </tr>
            <tr>
                <td align="center">
                    <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/downloaded.png"><img alt="Downloaded files" src="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/downloaded.png" width="300"/></a>
                    <br><em>Downloaded files (dark mode)</em>
                </td>
                <td align="center">
                    <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/downloaded_period.png"><img alt="Downloaded files" src="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/downloaded_period.png" width="300"/></a>
                    <br><em>Downloaded files with date range filter (dark mode)</em>
                </td>
                <td align="center">
                    <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/uploaded.png"><img alt="Uploaded torrents" src="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/uploaded.png" width="300"/></a>
                    <br><em>Uploaded torrents (light mode)</em>
                </td>
            </tr>
            <tr>
                <td align="center">
                    <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/stats.png"><img alt="Statistics" src="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/stats.png" width="300"/></a>
                    <br><em>Statistics (dark mode)</em>
                </td>
                <td align="center">
                    <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/info.png"><img alt="Informations" src="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/info.png" width="300"/></a>
                    <br><em>info (dark mode)</em>
                </td>
                <td align="center">
                    <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/settings.png"><img alt="Statistics" src="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/settings.png" width="300"/></a>
                    <br><em>Settings for SeedboxSync (light mode)</em>
                </td>
            </tr>
            <tr>
                <td align="center">
                    <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/settings_seedbox.png"><img alt="Statistics" src="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/settings_seedbox.png" width="300"/></a>
                    <br><em>Settings for Seedbox (dark mode)</em>
                </td>
                <td align="center">
                    <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/users_list.png"><img alt="Statistics" src="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/users_list.png" width="300"/></a>
                    <br><em>Users list (dark mode)</em>
                </td>
                <td align="center">
                    <a href="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/api-spec.png"><img alt="API SPEC" src="https://raw.githubusercontent.com/llaumgui/seedboxsync/refs/heads/main/docs/images/screenshots/api-spec.png" width="300"/></a>
                    <br><em>API</em>
                </td>
            </tr>
        </table>
    </div>
</details>

## Full documentation

See: [https://llaumgui.github.io/seedboxsync/](https://llaumgui.github.io/seedboxsync/)

## Build with

<p style="text-align:center;">
  <a href="https://www.python.org"><img alt="Python logo" src="docs/images/python-powered-w-140x56.png" /></a> <a href="https://flask.palletsprojects.com"><img alt="Flask logo" src="docs/images/logo-flask.png" /></a> <a href="https://docs.peewee-orm.com"><img alt="peewee logo" src="docs/images/logo-peewee.png" /></a>
</p>

## License

Released under the [GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html).

[ico-bluesky]: https://img.shields.io/static/v1?label=Author&message=llaumgui&color=208bfe&logo=bluesky&style=flat-square
[link-bluesky]: https://bsky.app/profile/llaumgui.kulakowski.fr
[ico-ghactions]: https://img.shields.io/github/actions/workflow/status/llaumgui/seedboxsync/build-test-deploy.yml?branch=main&style=flat-square&logo=github&label=Build
[link-ghactions]: https://github.com/llaumgui/seedboxsync/actions
[ico-pypi-version]: https://img.shields.io/pypi/v/seedboxsync?include_prereleases&label=Package%20version&style=flat-square&logo=python
[link-pypi]:https://pypi.org/project/seedboxsync/
[ico-license]: https://img.shields.io/github/license/llaumgui/seedboxsync?style=flat-square
[ico-docker]: https://img.shields.io/docker/pulls/llaumgui/seedboxsync?color=%2496ed&logo=docker&style=flat-square
[link-docker]: https://hub.docker.com/r/llaumgui/seedboxsync
[ico-version]: https://img.shields.io/docker/v/llaumgui/seedboxsync?sort=semver&color=%2496ed&logo=docker&style=flat-square
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
