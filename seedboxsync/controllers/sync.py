# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

import datetime
import glob
import os
import re
from paramiko import SSHException
from cement import Controller, ex, fs
from ..core.dao.torrent import Torrent
from ..core.dao.download import Download
from ..core.exc import SeedboxSyncConfigurationError


class Sync(Controller):
    class Meta:
        help = 'all synchronization operations'
        label = 'sync'
        stacked_on = 'base'
        stacked_type = 'nested'

    @ex(help='sync torrent from blackhole to seedbox',
        arguments=[(['--dry-run'],
                   {'help': 'just list, no upload and persistence',
                    'action': 'store_true',
                    'dest': 'dry_run'}),
                   (['-p', '--ping'],
                   {'help': 'ping a service (ie: Healthchecks) during excecution',
                    'action': 'store_true',
                    'dest': 'ping'})])
    def blackhole(self):
        """
        Do the blackhole synchronization.
        """
        self.app.log.debug('sync_blackhole dry-run: "%s"' % self.app.pargs.dry_run)

        # Call ping_start_hook
        if self.app.pargs.ping:
            for res in self.app.hook.run('ping_start_hook', self.app, 'sync_blackhole'):
                pass

        # Create lock file.
        lock_file = self.app.config.get('pid', 'blackhole_path')
        self.app.lock.lock_or_exit(lock_file)

        # Get all torrents
        torrents = glob.glob(fs.join(fs.abspath(self.app.config.get('local', 'watch_path')), '*.torrent'))
        if len(torrents) > 0:
            # Upload torrents one by one
            for torrent_file in torrents:
                torrent_name = os.path.basename(torrent_file)
                if not self.app.pargs.dry_run:
                    tmp_path = self.app.config.get('seedbox', 'tmp_path')
                    watch_path = self.app.config.get('seedbox', 'watch_path')

                    self.app.log.info('Upload torrent: "%s"' % torrent_name)
                    self.app.log.debug('Upload "%s" in "%s" directory' % (torrent_file, tmp_path))

                    try:
                        self.app.sync.put(torrent_file, os.path.join(tmp_path, torrent_name))

                        # Chmod
                        chmod = self.app.config.get('seedbox', 'chmod')
                        if chmod is not False:
                            self.app.log.debug('Change mod in %s' % chmod)
                            self.app.sync.chmod(os.path.join(tmp_path, torrent_name), int(chmod, 8))

                        # Move from tmp
                        self.app.log.debug('Move from "%s" to "%s"' % (tmp_path, watch_path))
                        self.app.sync.rename(os.path.join(tmp_path, torrent_name), os.path.join(watch_path, torrent_name))

                        # Store in DB
                        torrent_info = self.app.bcoding.get_torrent_infos(torrent_file)
                        torrent = Torrent.create(name=torrent_name)
                        if torrent_info is not None:
                            torrent.announce = torrent_info['announce']
                            torrent.save()

                            # Remove local torent
                            self.app.log.debug('Remove local torrent "%s"' % torrent_file)
                            os.remove(torrent_file)
                        else:
                            self.app.log.warning('Rename local "%s" to .torrent.fail' % torrent_file)
                            os.rename(torrent_file, torrent_file + '.fail')
                    except SSHException as exc:
                        self.app.log.warning('SSH client exception > %s' % str(exc))

                else:
                    self.app.log.info('Not upload torrent: "%s"' % torrent_name)
        else:
            self.app.log.info('No torrent in "%s"' % self.app.config.get('local', 'watch_path'))

        # Remove lock file.
        self.app.lock.unlock(lock_file)

        # Call ping_start_hook
        if self.app.pargs.ping:
            for res in self.app.hook.run('ping_success_hook', self.app, 'sync_blackhole'):
                pass

    @ex(help='sync file from seedbox',
        arguments=[(['--dry-run'],
                   {'help': 'just list, no download and persistence',
                    'action': 'store_true',
                    'dest': 'dry_run'}),
                   (['-o', '--only-store'],
                   {'help': 'just store the list, no download. Usefull to sync from an already synchronized seedbox',
                    'action': 'store_true',
                    'dest': 'only_store'}),
                   (['-p', '--ping'],
                   {'help': 'ping a service (ie: Healthchecks) during excecution',
                    'action': 'store_true',
                    'dest': 'ping'})])
    def seedbox(self):
        """
        Do the synchronization.
        """

        # Call ping_start_hook
        if self.app.pargs.ping:
            for res in self.app.hook.run('ping_start_hook', self.app, 'sync_seedbox'):
                pass

        self.app.log.debug('sync_blackhole dry-run: "%s"' % self.app.pargs.dry_run)
        self.app.log.debug('sync_blackhole only-store: "%s"' % self.app.pargs.only_store)

        # Create lock file.
        lock_file = self.app.config.get('pid', 'download_path')
        self.app.lock.lock_or_exit(lock_file)

        finished_path = self.app.config.get('seedbox', 'finished_path')
        part_suffix = self.app.config.get('seedbox', 'part_suffix')
        self.app.log.debug('Get file list in "%s"' % finished_path)

        # Get all files
        try:
            self.app.sync.chdir(finished_path)
            for walker in self.app.sync.walk(''):
                for filename in walker[2]:
                    filepath = os.path.join(walker[0], filename)
                    if os.path.splitext(filename)[1] == part_suffix:
                        self.app.log.debug('Skip part file "%s"' % filename)
                    elif Download.is_already_download(filepath):
                        self.app.log.debug('Skip already downloaded "%s"' % filename)
                    elif self.__exclude_by_pattern(filepath):
                        self.app.log.debug('Skip excluded by pattern "%s"' % filename)
                    else:
                        if not self.app.pargs.dry_run:
                            self.__get_file(filepath)
                        else:
                            self.app.log.info('Not download "%s"' % filepath)
        except (IOError, FileNotFoundError) as exc:
            self.app.log.error('SeedboxSyncError > "%s"' % exc)

        # Remove lock file.
        self.app.lock.unlock(lock_file)

        # Call ping_start_hook
        if self.app.pargs.ping:
            for res in self.app.hook.run('ping_success_hook', self.app, 'sync_seedbox'):
                pass

    def __get_file(self, filepath):
        """
        Download a single file.

        :param str filepath: the filepath
        """
        # Local path (without seedbox folder prefix)
        local_filepath = fs.join(self.app.config.get('local', 'download_path'), filepath)
        part_suffix = self.app.config.get('seedbox', 'part_suffix')
        local_filepath_part = local_filepath + part_suffix
        local_path = os.path.dirname(fs.abspath(local_filepath))

        # Make folder tree
        if not self.app.pargs.only_store:
            fs.ensure_dir_exists(local_path)
        self.app.log.debug('Download: "%s" in "%s"' % (filepath, local_path))

        try:
            # Start timestamp in database
            seedbox_size = self.app.sync.stat(filepath).st_size
            if seedbox_size == 0:
                self.app.log.warning('Empty file: "%s" (%s)' % (filepath, str(seedbox_size)))

            download = Download.create(path=filepath,
                                       seedbox_size=seedbox_size)
            download.save()

            # Get file with ".part" suffix
            if not self.app.pargs.only_store:
                self.app.log.info('Download "%s"' % filepath)
                self.app.sync.get(filepath, local_filepath_part)
                local_size = os.stat(local_filepath_part).st_size

                # Test size of the downloaded file
                if (local_size == 0) or (local_size != seedbox_size):
                    self.app.log.error('Download fail: "%s" (%s/%s)' % (filepath, str(local_size), str(seedbox_size)))
                    return False

                # All is good ! Remove ".part" suffix
                os.rename(local_filepath_part, local_filepath)
            else:
                self.app.log.info('Mark as downloaded "%s"' % filepath)
                local_size = seedbox_size

            # Store in database
            download.local_size = local_size
            download.finished = datetime.datetime.now()
            download.save()
        except SSHException as exc:
            self.app.log.error('Download fail: %s' % str(exc))

    def __exclude_by_pattern(self, filepath: str):
        """
        Allow to exclude sync by pattern

        :param str filepath: the filepath
        """
        pattern = self.app.config.get('seedbox', 'exclude_syncing')
        if pattern == "":
            return False

        try:
            match = re.search(pattern, filepath)
        except re.error:
            raise SeedboxSyncConfigurationError('Bad configuration for exclude_syncing ! See the doc at https://docs.python.org/3/library/re.html')

        if match is None:
            return False
        else:
            return True
