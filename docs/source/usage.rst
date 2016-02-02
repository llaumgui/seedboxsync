Usage
=====

In command line
---------------
.. code-block:: bash

    usage: seedboxsync [-h] [--blackhole | -t [LASTS_TORRENTS] | --download | -d
                       [LASTS_DOWNLOADS] | -u] [-q]

    Script for sync operations between your NAS and your seedbox.

    optional arguments:
      -h, --help            show this help message and exit
      --blackhole           send torrent from the local blackhole to the seedbox
                            blackhole
      -t [LASTS_TORRENTS], --lasts-torrents [LASTS_TORRENTS]
                            get list of lasts torrents uploaded
      --download            download finished files from seedbox to NAS
      -d [LASTS_DOWNLOADS], --lasts-downloads [LASTS_DOWNLOADS]
                            get list of lasts downloads
      -u, --unfinished-downloads
                            get list of unfinished downloads
      -q, --quiet


In crontab
----------
.. code-block:: bash

    # Sync blackhole every 2mn
    */2 * * * * root seedboxsync --blackhole

    # Download torrents finished every 15mn
    */15 * * * * root seedboxsync.py --download

You can also add a logrotate configuration in /etc/logrotate.d/seedboxsync:

.. code-block:: bash

    /var/log/seedboxsync_*.log {
        weekly
        missingok
        rotate 4
        compress
        notifempty
    }


.. toctree::
   :maxdepth: 2