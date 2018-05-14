Configuration
=============

Configuration file
------------------
You can use the example configuration file. This file can be located in:

* /usr/local/etc/ (pip install)
* ~/.local/etc/ (pip install in user privileges)
* /opt/llaumgui/seedboxsync (clone repository)

.. code-block:: bash

    sudo cp /usr/local/etc/seedbox.ini.dist /etc/seedbox.ini

You can put your configuration in:

* seedboxsync.ini in the root of the sources folder.
* ~/.seedboxsync/seedboxsync.ini
* /usr/local/etc/seedboxsync.ini
* /usr/local/etc/seedboxsync/seedboxsync.ini
* /etc/seedboxsync.ini
* /etc/seedboxsync/seedboxsync.ini

.. toctree::
   :maxdepth: 2

Settings
--------

Configuration about your seedbox and your BitTorrent client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* First, set informations about the connection to your Seedbox. Currently, only sftp is supported.

.. code-block:: ini

    [Seedbox]

    # Informations about your seedbox connection
    transfer_host=my-seedbox.net
    transfer_port=22
    transfer_login=me
    transfer_password=p4sw0rd

    # For the moment, only sftp
    transfer_protocol=sftp

* To prevent some issues between your transfer account and your BitTorrent client account, SeedboxSync chmod torrent file after upload.

.. code-block:: ini

    # Chmod torrent after upload (false = disable)
    # Use octal notation like https://docs.python.org/3.4/library/os.html#os.chmod
    transfer_chmod=0o777

* To prevent that your BitTorrent client watch (and use) an incomplete torrent file, SeedboxSync transfer torrent file in a tmp directory (tmp_path) and move it in the watch folder after full transfert and chmod. The tmp folder must also be used in your BitTorrent client to download unfinished torrent.

.. figure::  _static/rutorrent_1.png
   :align:   center

.. code-block:: ini

    # Use a tempory directory (you must create it !)
    tmp_path=/tmp

* The blackhole folder of your BitTorrent client. Only used by blackhole synchronisation.

.. code-block:: ini

    # Your "watch" folder you must create it!)
    watch_path=/watch

* The folder of your Bittorrent client with finished file. You can configure your client to move finished file in a specific folder.

.. figure::  _static/rutorrent_2.png
   :align:   center

.. code-block:: ini

    # Your finished folder you must create it!)
    finished_path=/files

* You can remove a prefix part of the path in your synced directory.

.. code-block:: ini

    # Allow to remove a part of the synced path. In General, same path than "finished_path".
    prefixed_path=/files

* You can also specified extension used by your torrent client for downloads in progress to exclude it from synchronisation.

.. code-block:: ini

    # Exclude part files
    part_suffix=.part

* You can also exclude files from sync with regular expression.

.. code-block:: ini

    # Exclude pattern from sync
    # Use re syntaxe: https://docs.python.org/3/library/re.html
    # Example: .*missing$|^\..*\.swap$
    exclude_syncing=


Configuration about your NAS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Configuration aboout local folders:
    * watch_path: The local blackhole used for blackhole synchronisation.
    * download_path: the folder where download finished torrent.
    * sqlite_path: where to store all information about transfer (used sqlite).

.. code-block:: ini

    [Local]
    # Your local "watch" folder
    watch_path=/home/bittorrent/watch

    # Path where download files
    download_path=/home/bittorent/Download/

    # Use local sqlite database for store downloaded files
    sqlite_path=/var/opt/seedboxsync/seedboxsync.sql

* All informations about log and pid files:

.. code-block:: ini

    [Log]
    blackhole_file_path=/var/log/seedboxsync_blackhole.log
    download_file_path=/var/log/seedboxsync_download.log
    blackhole_level=INFO
    download_level=INFO


    [PID]
    blackhole_path=/var/run/seedboxsync_blackhole.pid
    download_path=/var/run/seedboxsync_download.pid