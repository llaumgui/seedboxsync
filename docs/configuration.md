---
layout: page
title: Configuration
description: ~
order: 2
---

## Configuration file

You can use [the example configuration file](https://github.com/llaumgui/seedboxsync/blob/main/config/seedboxsync.yml.example). This example file can be located in:

* /usr/local/config/ (pip install)
* ~/.local/config/ (pip install in user privileges)

```bash
mkdir ~/.config/seedboxsync
cp ~/.local/config/seedboxsync.yml.example ~/.config/seedboxsync/seedboxsync.yml
```

or

```bash
sudo mkdir /etc/seedboxsync
sudo cp /usr/local/config/seedboxsync.yml.example /etc/seedboxsync/seedboxsync.yml
```

You can put your configuration in:

* /etc/seedboxsync/seedboxsync.yml
* ~/.config/seedboxsync/seedboxsync.yml
* ~/.seedboxsync/config/seedboxsync.yml
* ~/.seedboxsync.yml

## Settings

### Configuration about your seedbox and your BitTorrent client

* First, set informations about the connection to your Seedbox. Currently, only sftp is supported.

```yml
#
# Informations about your seedbox
#
seedbox:

  ### Informations about your seedbox connection
  host: my-seedbox.ltd
  port: 22
  login: me
  password: p4sw0rd

  ### For the moment, only sftp
  protocol: sftp
```

* To prevent some issues between your transfer account and your BitTorrent client account, SeedboxSync chmod torrent file after upload.

```yml
    ### Chmod torrent after upload (false :  disable)
    ### Use octal notation like https://docs.python.org/3.4/library/os.html#os.chmod
    chmod: false
```

* To prevent that your BitTorrent client watch (and use) an incomplete torrent file, SeedboxSync transfer torrent file in a tmp directory (```tmp\_path```) and move it in the watch folder after full transfert and chmod. The tmp folder must also be used in your BitTorrent client to download unfinished torrent.

![ruTorrent settings / Downloads](images/rutorrent_1.png)

```yml
    # Use a tempory directory (you must create it !)
    tmp_path: /tmp
```

* The blackhole folder of your BitTorrent client. Only used by blackhole synchronisation.

```yml
    # Your "watch" folder you must create it!)
    watch_path: /watch
```

* The folder of your Bittorrent client with finished file. You can configure your client to move finished file in a specific folder.

![ruTorrent settings / Autotools](images/rutorrent_2.png)

```yml
    # Your finished folder you must create it!)
    finished_path: /files
```

* You can remove a prefix part of the path in your synced directory.

```yml
    # Allow to remove a part of the synced path. In General, same path than "finished_path".
    prefixed_path: /files
```

* You can also specified extension used by your torrent client for downloads in progress to exclude it from synchronisation.

```yml
    # Exclude part files
    part_suffix: .part
```

* You can also exclude files from sync with regular expression.

```yml
    # Exclude pattern from sync
    # Use re syntaxe: https://docs.python.org/3/library/re.html
    # Example: .*missing$|^\..*\.sw
    exclude_syncing: .*missing$|^\..*\.sw
```

### Configuration about your NAS

Your NAS configuration is in local and pid sections:

```yml
#
# Informations about local environment (NAS ?)
#
local:

  ### Your local "watch" folder
  watch_path: ~/watch

  ### Path where download files
  download_path: ~/Downloads/

  ### Use local sqlite database for store downloaded files
  db_file: ~/.config/seedboxsync/seedboxsync.db


#
# PID and lock management to prevent several launch
#
pid:

    ### PID for blackhole sync
    blackhole_path: ~/.config/seedboxsync/lock/blackhole.pid

    ### PID for seedbox downloaded sync
    download_path: ~/.config/seedboxsync/lock/download.pid

```

### Configuration of a ping service

Ping service is called by `--ping` argument.

Currently only [Healthchecks](https://github.com/healthchecks/healthchecks) ping service is supported.

#### Healthchecks

Add a healthchecks by sync command.

```yml
#
# Healthchecks ping service
#
healthchecks:

  ### sync seedbox part
  sync_seedbox:
    ## Enable or disable service
    enabled: true

    ## Ping URL
    ping_url: https://hc-ping.com/ca5e1159-9acf-410c-9202-f76a7bb856e0

  ### sync blackhole part
  sync_blackhole:
    ## Enable or disable service
    enabled: true

    ## Ping URL
    ping_url: https://hc-ping.com/ca5e1159-9acf-410c-9202-f76a7bb856e0
```
