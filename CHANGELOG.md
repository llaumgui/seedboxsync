# ChangeLog

## Next release

* Todo

## 3.1.0 - May 30, 2025

> ⚠ **Warning:** Docker is now the recommended method.

* 👷 Add docker support and provide docker images.
* ⬆️ Update Cement framework.
* 📦 Fix packaging issues.
* 📝 Add Changelog and Contributors files.
* 💚 Fix SonarCloud.
* 👷 Drop Python 3.7 support.
* 👷 Drop Python 3.8 support.
* ⬆️ Now support Python version from 3.9 to 3.13.

## 3.0.1 - Feb 14, 2022

* [Enhancement #36](https://github.com/llaumgui/seedboxsync/issues/36) Update Cement framework.
* [Bug #38](https://github.com/llaumgui/seedboxsync/issues/38) ::set-env is now deprecated.
* [Bug #35](https://github.com/llaumgui/seedboxsync/issues/35) Fix SonarCloud analysis.

## 3.0.0 (Cement / peewee full rebuild) - Sep 23, 2020

*SeedboxSync v1 was the first release on Python 2, SeedboxSync v2 was port from Python 2 code to a compatible Python 3 code and SeedboxSync v3 is a full rewrite on [https://builtoncement.com/](Cement framework) and Peepee ORM.*

Change since v2 serie:

* [Enhancement #27](https://github.com/llaumgui/seedboxsync/issues/27) Rebuild on Cement.
* [Enhancement #29](https://github.com/llaumgui/seedboxsync/issues/29) Add ORM support: Use Peepee ORM.
* [Enhancement #26](https://github.com/llaumgui/seedboxsync/issues/26) New CI/CD platform and features part 2: release with GitHub Actions.
* [Enhancement #30](https://github.com/llaumgui/seedboxsync/issues/30) Better list-in-progress: Add percentage and time prediction.
* [Bugfix #14](https://github.com/llaumgui/seedboxsync/issues/14) No timeout on connections.
* [Enhancement #34](https://github.com/llaumgui/seedboxsync/issues/34) Add ping architecture and Healthchecks support.

## 3.0.0b3 - Sep 15, 2020

Bugfix

## 3.0.0b2 - Sep 4, 2020

Second beta.

* Update documentation.
* Update code.
* [Enhancement #34](https://github.com/llaumgui/seedboxsync/issues/34) Add ping architecture and Healthchecks support.

## 3.0.0b1 - Aug 26, 2020

* [Enhancement #27](https://github.com/llaumgui/seedboxsync/issues/27) Rebuild on Cement.
* [Enhancement #29](https://github.com/llaumgui/seedboxsync/issues/29) Add ORM support: Use Peepee ORM.
* [Enhancement #26](https://github.com/llaumgui/seedboxsync/issues/26) New CI/CD platform and features part 2: release with GitHub Actions.
* [Enhancement #30](https://github.com/llaumgui/seedboxsync/issues/30) Better list-in-progress: Add percentage and time prediction.
* [Bugfix #14](https://github.com/llaumgui/seedboxsync/issues/14) No timeout on connections.

## 2.0.1 - Nov 1, 2018

* [Enhancement #22](https://github.com/llaumgui/seedboxsync/issues/22) Migration from Sphinx to GitHub documentation.
* [Enhancement #23](https://github.com/llaumgui/seedboxsync/issues/23) File size check, don't exist.
* [Enhancement #24](https://github.com/llaumgui/seedboxsync/issues/24) New version system.

## 2.0.0 (Python3) - May 29, 2018

Changes since v1 serie:

* The big change: #12 Python 3 support:
  * [Enhancement] Python 3 enhancements.
  * [Enhancement] Replace bencode by bcoding because Python 3.
  * [Enhancement] Update Paramiko requirement (>=2.2.1).
* Others enhancements:
  * [Enhancement] Better usage of configparser.
  * [Enhancement #19](https://github.com/llaumgui/seedboxsync/issues/19) Use exception instead exit.
* New features:
  * [Enhancement #20](https://github.com/llaumgui/seedboxsync/issues/20) Sync exclusion.
  * [Enhancement] New logo.
* QA:
  * [Bug] Doc building from Travis. Doc is updated ! See: <https://llaumgui.github.io/seedboxsync/>.
  * Use tox for QA and tests.
  * Update Travis config.
  * Update Code Climate config.

## 2.0.0.beta2 (Last beta ?) - May 15, 2018

* [Enhancement #19](https://github.com/llaumgui/seedboxsync/issues/19) Use exception instead exit.
* [Enhancement #20](https://github.com/llaumgui/seedboxsync/issues/20) Sync Exclusion.
* [Enhancement] New logo.

## 2.0.0.beta1 (Python3 usable !) - Aug 17, 2017

* [Enhancement #15] Replace BencodePy by bcoding to fix --blackhole issue.
* [Bug] Doc building from Travis. Doc is updated ! See: <https://llaumgui.github.io/seedboxsync/>.

## 1.1.2 (The last Python 2 version ?) - Jul 22, 2017

* Some cleanup before archive.
* Backport "prefixed_path" from Python3 branch.

## 2.0.0.alpha1 (First Python3 version !) - Jul 22, 2017

* [Enhancement #12](https://github.com/llaumgui/seedboxsync/issues/12) Python 3 suppport.
* [Enhancement] Python 3 enhancement.
* [Enhancement] Replace bencode by bencodepy because Py3.
* [Enhancement] Update Paramiko requirement (>=2.2.1).
* [Enhancement] Better use of configparser.
* [Enhancement] More Try / except.

## 1.1.1 - Feb 17, 2016

* [Enhancement #13](https://github.com/llaumgui/seedboxsync/issues/13) Better documenttion.
* [Bugfix #13](https://github.com/llaumgui/seedboxsync/issues/13) Typo fix in seedboxsync.ini.

Important: update your seedboxsync.ini and replace wath_path by watch_path.

## 1.1.0 - Feb 4, 2016

* [Enhancement #10](https://github.com/llaumgui/seedboxsync/issues/10): Make code documentation: <https://llaumgui.github.io/seedboxsync>.
* [Enhancement #9](https://github.com/llaumgui/seedboxsync/issues/9): Check if the process inside the PID lock file is still running (thanks @johanndt).
* [Enhancement #3](https://github.com/llaumgui/seedboxsync/issues3): Use a transport interface: you can now make a PR for FTP support ;-).

## 1.0.0 - Oct 13, 2015

First stable version.

## 0.9.0 (a.k.a v1.0.0 RC1) - Aug 20, 2015

First version avalaible from Pypi.

* [enhancement #1](https://github.com/llaumgui/seedboxsync/issues/1): Install seedboxsync with a setup.py.
* [enhancement #2](https://github.com/llaumgui/seedboxsync/issues/2): Check size after download.
* [enhancement #4](https://github.com/llaumgui/seedboxsync/issues/4): Allow shorts arguments.
* [Bug #5](https://github.com/llaumgui/seedboxsync/issues/5): Download fail: cannot concatenate 'str' and 'int' objects.

## 0.5.0 (Full rewrite) - Aug 14, 2015

Pre-release v0.5.0, first release just after a full rewrite.

## 0.1.0 (Pre-release) - Aug 8, 2015

First quick and not so dirty release before an full rewrite.
