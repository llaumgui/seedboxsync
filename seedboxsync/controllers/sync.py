# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
Controller responsible for synchronization operations between local NAS
and the remote seedbox.
"""

import datetime
import glob
import os
import re
from paramiko import SSHException  # type: ignore[import-untyped]
from cement import Controller, ex, fs  # type: ignore[attr-defined]
from seedboxsync.core.dao import Download, Torrent
from seedboxsync.core.exc import SeedboxSyncConfigurationError


class Sync(Controller):
    """
    Synchronization controller.

    Handles operations such as uploading torrents from blackhole
    and downloading files from the seedbox, with optional dry-run mode
    and ping hooks for monitoring.
    """
    class Meta:
        help = 'all synchronization operations'
        label = 'sync'
        stacked_on = 'base'
        stacked_type = 'nested'

    @ex(help='sync torrent from blackhole to seedbox',
        arguments=[(['--dry-run'],
                   {'help': 'list only, do not upload or persist files',
                    'action': 'store_true',
                    'dest': 'dry_run'}),
                   (['-p', '--ping'],
                   {'help': 'ping a service (e.g., Healthchecks) during execution',
                    'action': 'store_true',
                    'dest': 'ping'})])
    def blackhole(self) -> None:
        """
        Perform the blackhole synchronization.

        Uploads torrent files from the local watch folder to the seedbox.
        Handles creation of lock files, optional dry-run, file permissions,
        database persistence, and error handling.
        """
        self.app.log.debug('sync_blackhole dry-run: "%s"' % self.app.pargs.dry_run)

        # Call ping_start_hook if enabled
        if self.app.pargs.ping:
            for res in self.app.hook.run('ping_start_hook', self.app, 'sync_blackhole'):
                pass

        # Create lock
        self.app.lock.lock_or_exit('sync_blackhole')  # type: ignore[attr-defined]

        # Gather all torrent files
        torrents = glob.glob(fs.join(fs.abspath(self.app.config.get('local', 'watch_path')), '*.torrent'))
        if len(torrents) > 0:
            for torrent_file in torrents:
                torrent_name = os.path.basename(torrent_file)
                if not self.app.pargs.dry_run:
                    tmp_path = self.app.config.get('seedbox', 'tmp_path')
                    watch_path = self.app.config.get('seedbox', 'watch_path')

                    self.app.log.info('Upload torrent: "%s"' % torrent_name)
                    self.app.log.debug('Upload "%s" to "%s"' % (torrent_file, tmp_path))

                    try:
                        self.app.sync.put(torrent_file, os.path.join(tmp_path, torrent_name))  # type: ignore[attr-defined]

                        # Apply chmod if configured
                        chmod = self.app.config.get('seedbox', 'chmod')
                        if chmod is not False:
                            self.app.log.debug('Change permissions to %s' % chmod)
                            self.app.sync.chmod(os.path.join(tmp_path, torrent_name), int(chmod, 8))  # type: ignore[attr-defined]

                        # Move file from tmp to watch directory
                        self.app.log.debug('Move from "%s" to "%s"' % (tmp_path, watch_path))
                        self.app.sync.rename(os.path.join(tmp_path, torrent_name), os.path.join(watch_path, torrent_name))  # type: ignore[attr-defined]

                        # Store torrent info in database
                        torrent_info = self.app.bcoding.get_torrent_infos(torrent_file)  # type: ignore[attr-defined]
                        torrent = Torrent.create(name=torrent_name)
                        if torrent_info is not None:
                            torrent.announce = torrent_info['announce']
                            torrent.save()

                            # Remove local torrent file
                            self.app.log.debug('Remove local torrent "%s"' % torrent_file)
                            os.remove(torrent_file)
                        else:
                            self.app.log.warning('Rename local "%s" to .torrent.fail' % torrent_file)
                            os.rename(torrent_file, torrent_file + '.fail')
                    except SSHException as exc:
                        self.app.log.warning('SSH client exception > %s' % str(exc))
                else:
                    self.app.log.info('Dry-run: not uploading torrent "%s"' % torrent_name)
        else:
            self.app.log.info('No torrent files found in "%s"' % self.app.config.get('local', 'watch_path'))

        # Remove lock
        self.app.lock.unlock('sync_blackhole')  # type: ignore[attr-defined]

        # Call ping_success_hook if enabled
        if self.app.pargs.ping:
            for res in self.app.hook.run('ping_success_hook', self.app, 'sync_blackhole'):
                pass

    @ex(help='sync files from seedbox',
        arguments=[(['--dry-run'],
                   {'help': 'list only, do not download or persist files',
                    'action': 'store_true',
                    'dest': 'dry_run'}),
                   (['-o', '--only-store'],
                   {'help': 'store the file list only, no download; useful for already synced seedbox',
                    'action': 'store_true',
                    'dest': 'only_store'}),
                   (['-p', '--ping'],
                   {'help': 'ping a service (e.g., Healthchecks) during execution',
                    'action': 'store_true',
                    'dest': 'ping'})])
    def seedbox(self) -> None:
        """
        Perform synchronization from the seedbox.

        Downloads files from the remote seedbox to the local machine,
        supports optional dry-run and only-store modes, applies exclusion patterns,
        and persists download information in the database.
        """
        # Call ping_start_hook if enabled
        if self.app.pargs.ping:
            for res in self.app.hook.run('ping_start_hook', self.app, 'sync_seedbox'):
                pass

        self.app.log.debug('sync_seedbox dry-run: "%s"' % self.app.pargs.dry_run)
        self.app.log.debug('sync_seedbox only-store: "%s"' % self.app.pargs.only_store)

        # Create lock
        self.app.lock.lock_or_exit('sync_seedbox')  # type: ignore[attr-defined]

        finished_path = self.app.config.get('seedbox', 'finished_path')
        part_suffix = self.app.config.get('seedbox', 'part_suffix')
        self.app.log.debug('Scanning files in "%s"' % finished_path)

        # Walk through all files on the seedbox
        try:
            self.app.sync.chdir(finished_path)  # type: ignore[attr-defined]
            for walker in self.app.sync.walk(''):  # type: ignore[attr-defined]
                for filename in walker[2]:
                    filepath = os.path.join(walker[0], filename)
                    if os.path.splitext(filename)[1] == part_suffix:
                        self.app.log.debug('Skipping part file "%s"' % filename)
                    elif Download.is_already_download(filepath):
                        self.app.log.debug('Skipping already downloaded file "%s"' % filename)
                    elif self.__exclude_by_pattern(filepath):
                        self.app.log.debug('Skipping excluded file "%s"' % filename)
                    else:
                        if not self.app.pargs.dry_run:
                            self.__get_file(filepath)
                        else:
                            self.app.log.info('Dry-run: not downloading "%s"' % filepath)
        except (IOError, FileNotFoundError) as exc:
            self.app.log.error('SeedboxSyncError > "%s"' % exc)

        # Remove lock
        self.app.lock.unlock('sync_seedbox')  # type: ignore[attr-defined]

        # Call ping_success_hook if enabled
        if self.app.pargs.ping:
            for res in self.app.hook.run('ping_success_hook', self.app, 'sync_seedbox'):
                pass

    def __get_file(self, filepath: str) -> None:
        """
        Download a single file from the seedbox.

        Handles file path creation, partial download suffix, database persistence,
        size verification, and renaming after successful download.

        Args:
            filepath (str): Path of the file on the seedbox.
        """
        local_filepath = fs.join(self.app.config.get('local', 'download_path'), filepath)
        part_suffix = self.app.config.get('seedbox', 'part_suffix')
        local_filepath_part = local_filepath + part_suffix
        local_path = os.path.dirname(fs.abspath(local_filepath))

        # Create local directory tree if necessary
        if not self.app.pargs.only_store:
            fs.ensure_dir_exists(local_path)
        self.app.log.debug('Download: "%s" to "%s"' % (filepath, local_path))

        try:
            seedbox_size = self.app.sync.stat(filepath).st_size  # type: ignore[attr-defined]
            if seedbox_size == 0:
                self.app.log.warning('Empty file: "%s" (%s)' % (filepath, str(seedbox_size)))

            download = Download.create(path=filepath, seedbox_size=seedbox_size)
            download.save()

            if not self.app.pargs.only_store:
                self.app.log.info('Downloading "%s"' % filepath)
                self.app.sync.get(filepath, local_filepath_part)  # type: ignore[attr-defined]
                local_size = os.stat(local_filepath_part).st_size

                if local_size == 0 or local_size != seedbox_size:
                    self.app.log.error('Download failed: "%s" (%s/%s)' % (filepath, str(local_size), str(seedbox_size)))

                os.rename(local_filepath_part, local_filepath)
            else:
                self.app.log.info('Marking as downloaded "%s"' % filepath)
                local_size = seedbox_size

            download.local_size = local_size
            download.finished = datetime.datetime.now()
            download.save()
        except SSHException as exc:
            self.app.log.error('Download failed: %s' % str(exc))

    def __exclude_by_pattern(self, filepath: str) -> bool:
        """
        Determine if a file should be excluded from synchronization based on patterns.

        Args:
            filepath (str): Path of the file to check.

        Returns:
            bool: True if the file matches the exclude pattern, False otherwise.

        Raises:
            SeedboxSyncConfigurationError: If the exclude pattern is invalid.
        """
        pattern = self.app.config.get('seedbox', 'exclude_syncing')
        if pattern == "":
            return False

        try:
            match = re.search(pattern, filepath)
        except re.error:
            raise SeedboxSyncConfigurationError('Invalid configuration for exclude_syncing! See https://docs.python.org/3/library/re.html')

        return match is not None
