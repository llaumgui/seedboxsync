# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
All commands related to synchronization operations in SeedboxSync.
"""

import click
import datetime
import glob
import os
import re
from paramiko import SSHException
from seedboxsync.core.dao import Download, Torrent
from seedboxsync.core.utils import get_torrent_infos
from seedboxsync.core.sync import DownloadProgress
from seedboxsync.core import fs
from seedboxsync.cli.exception import SeedboxSyncConfigurationError
from seedboxsync.cli import group, pass_context, Context


@group("sync", help="All synchronization operations.")  # type: ignore[untyped-decorator]
def cli() -> None:
    pass


@cli.command("blackhole", help="Sync torrent from blackhole to seedbox.")  # type: ignore[untyped-decorator]
@click.option(
    "--dry-run",
    help="List only, do not upload or persist files.",
    is_flag=True,
    default=False,
)
@click.option(
    "-p",
    "--ping",
    help="Ping a service (e.g., Healthchecks) during execution.",
    is_flag=True,
    default=False,
)
@pass_context
def blackhole(ctx: Context, dry_run: bool, ping: bool) -> None:
    """
    Perform the blackhole synchronization.

    Uploads torrent files from the local watch folder to the seedbox.
    Handles creation of lock files, optional dry-run, file permissions,
    database persistence, and error handling.

    Args:
        ctx (Context): The Click context object.
        dry_run (bool): Whether to perform a dry run.
        ping (bool): Whether to ping a service during execution.
    """
    if not ctx.app.seedboxsync_config.get("sync_blackhole_enabled") or False:
        ctx.app.logger.info("Blackhole synchronization task is disabled")
        ctx.exit(0)

    ctx.app.logger.debug('blackhole dry-run: "%s"' % dry_run)
    # Call ping_start_hook if enabled
    if ping:
        ctx.ping.start("sync_blackhole")

    # Create lock
    if not ctx.lock.lock_or_exit("sync_blackhole"):
        ctx.exit(0)

    # Gather all torrent files
    local_watch_path = ctx.app.seedboxsync_config.get("local_watch_path") or ""
    ctx.app.logger.debug('Scanning for torrent files in "%s"' % local_watch_path)
    torrents = glob.glob(fs.join(fs.abspath(local_watch_path), "*.torrent"))
    if len(torrents) > 0:
        for torrent_file in torrents:
            torrent_name = os.path.basename(torrent_file)
            if not dry_run:
                tmp_path = ctx.app.seedboxsync_config.get("seedbox_tmp_path") or ""
                watch_path = ctx.app.seedboxsync_config.get("seedbox_watch_path") or ""

                ctx.app.logger.info('Upload torrent: "%s"' % torrent_name)
                ctx.app.logger.debug('Upload "%s" to "%s"' % (torrent_file, tmp_path))

                try:
                    ctx.sync.put(torrent_file, os.path.join(tmp_path, torrent_name))

                    # Apply chmod if configured
                    chmod = ctx.app.seedboxsync_config.get("seedbox_chmod") or False
                    if isinstance(chmod, str):
                        ctx.app.logger.debug("Change permissions to %s" % chmod)
                        ctx.sync.chmod(os.path.join(tmp_path, torrent_name), int(chmod, 8))

                    # Move file from tmp to watch directory
                    ctx.app.logger.debug('Move from "%s" to "%s"' % (tmp_path, watch_path))
                    ctx.sync.rename(
                        os.path.join(tmp_path, torrent_name),
                        os.path.join(watch_path, torrent_name),
                    )

                    # Store torrent info in database
                    torrent_info = get_torrent_infos(torrent_file) or None
                    torrent = Torrent.create(name=torrent_name)
                    if torrent_info is not None and isinstance(torrent_info, dict):
                        torrent.announce = torrent_info.get("announce") or None
                        torrent.save()

                        # Remove local torrent file
                        ctx.app.logger.debug('Remove local torrent "%s"' % torrent_file)
                        os.remove(torrent_file)
                    else:
                        ctx.app.logger.warning('Rename local "%s" to .torrent.fail' % torrent_file)
                        os.rename(torrent_file, torrent_file + ".fail")
                except SSHException as exc:
                    ctx.app.logger.warning("SSH client exception > %s" % str(exc))
            else:
                ctx.app.logger.info('Dry-run: not uploading torrent "%s"' % torrent_name)
    else:
        ctx.app.logger.info('No torrent files found in "%s"' % ctx.app.seedboxsync_config.get("local_watch_path"))

    # Remove lock
    ctx.lock.unlock("sync_blackhole")

    # Call ping_success_hook if enabled
    ctx.ping.success("sync_blackhole")


@cli.command("seedbox", help="Sync files from seedbox.")  # type: ignore[untyped-decorator]
@click.option(
    "--dry-run",
    help="List only, do not upload or persist files.",
    is_flag=True,
    default=False,
)
@click.option(
    "-p",
    "--ping",
    help="Ping a service (e.g., Healthchecks) during execution.",
    is_flag=True,
    default=False,
)
@click.option(
    "-o",
    "--only-store",
    help="Store the file list only, no download; useful for already synced seedbox.",
    is_flag=True,
    default=False,
)
@pass_context
def seedbox(ctx: Context, dry_run: bool, ping: bool, only_store: bool) -> None:
    """
    Perform synchronization from the seedbox.

    Downloads files from the remote seedbox to the local machine,
    supports optional dry-run and only-store modes, applies exclusion patterns,
    and persists download information in the database.
    """
    if not ctx.app.seedboxsync_config.get("sync_seedbox_enabled") or False:
        ctx.app.logger.info("Seedbox synchronization task is disabled")
        ctx.exit(0)

    ctx.app.logger.debug('sync_seedbox dry-run: "%s"' % dry_run)
    ctx.app.logger.debug('sync_seedbox only-store: "%s"' % only_store)

    # Call ping_start_hook if enabled
    if ping:
        ctx.ping.start("sync_seedbox")

    # Create lock
    if not ctx.lock.lock_or_exit("sync_seedbox"):
        raise ctx.exit(0)

    finished_path = ctx.app.seedboxsync_config.get("seedbox_finished_path") or ""
    part_suffix = ctx.app.seedboxsync_config.get("seedbox_part_suffix")
    ctx.app.logger.debug('Scanning files in "%s"' % finished_path)

    # Walk through all files on the seedbox
    try:
        try:
            ctx.sync.chdir(finished_path)
        except FileNotFoundError as exc:
            ctx.app.logger.error(f"{str(exc)}\nFailed to scan directory: {finished_path}")
            return

        for walker in ctx.sync.walk(""):  # type: ignore[attr-defined]
            for filename in walker[2]:
                filepath = os.path.join(walker[0], filename)
                if os.path.splitext(filename)[1] == part_suffix:
                    ctx.app.logger.debug('Skipping part file "%s"' % filename)
                elif Download.is_already_download(filepath):
                    ctx.app.logger.debug('Skipping already downloaded file "%s"' % filename)
                elif __exclude_by_pattern(filepath):
                    ctx.app.logger.debug('Skipping excluded file "%s"' % filename)
                else:
                    if not dry_run:
                        __get_file(filepath, only_store)
                    else:
                        ctx.app.logger.info('Dry-run: not downloading "%s"' % filepath)
    except (IOError, FileNotFoundError) as exc:
        ctx.app.logger.error('SeedboxSyncError > "%s"' % exc)

    # Remove lock
    ctx.lock.unlock("sync_seedbox")

    # Call ping_success_hook if enabled
    if ping:
        ctx.ping.success("sync_seedbox")


@pass_context
def __get_file(ctx: Context, filepath: str, only_store: bool) -> None:
    """
    Download a single file from the seedbox.

    Handles file path creation, partial download suffix, database persistence,
    size verification, and renaming after successful download.

    Args:
        filepath (str): Path of the file on the seedbox.
    """
    local_filepath = fs.join(ctx.app.seedboxsync_config.get("local_download_path") or "", filepath)
    part_suffix = ctx.app.seedboxsync_config.get("seedbox_part_suffix") or ""
    local_filepath_part = local_filepath + part_suffix
    local_path = os.path.dirname(fs.abspath(local_filepath))

    # Create local directory tree if necessary
    if not only_store:
        fs.ensure_dir_exists(local_path)
    ctx.app.logger.debug('Download: "%s" to "%s"' % (filepath, local_path))

    try:
        seedbox_size = ctx.sync.stat(filepath).st_size  # type: ignore[attr-defined]
        if seedbox_size == 0:
            ctx.app.logger.warning('Empty file: "%s" (%s)' % (filepath, str(seedbox_size)))

        download = Download.create(path=filepath, seedbox_size=seedbox_size)
        download.save()

        if not only_store:
            ctx.app.logger.info('Downloading "%s"' % filepath)
            progress_callback = DownloadProgress(download)
            ctx.sync.get(filepath, local_filepath_part, progress_callback=progress_callback)
            local_size = os.stat(local_filepath_part).st_size

            if local_size == 0 or local_size != seedbox_size:
                ctx.app.logger.error('Download failed: "%s" (%s/%s)' % (filepath, str(local_size), str(seedbox_size)))

            os.rename(local_filepath_part, local_filepath)
        else:
            ctx.app.logger.info('Marking as downloaded "%s"' % filepath)
            local_size = seedbox_size

        download.local_size = local_size
        download.finished = datetime.datetime.now()
        download.save()
    except SSHException as exc:
        ctx.app.logger.error("Download failed: %s" % str(exc))


@pass_context
def __exclude_by_pattern(ctx: Context, filepath: str) -> bool:
    """
    Determine if a file should be excluded from synchronization based on patterns.

    Args:
        filepath (str): Path of the file to check.

    Returns:
        bool: True if the file matches the exclude pattern, False otherwise.

    Raises:
        SeedboxSyncConfigurationError: If the exclude pattern is invalid.
    """
    pattern = ctx.app.seedboxsync_config.get("seedbox_exclude_syncing") or ""
    if not pattern:
        return False

    try:
        return re.search(pattern, filepath) is not None
    except re.error:
        raise SeedboxSyncConfigurationError("Invalid configuration for exclude_syncing! See https://docs.python.org/3/library/re.html")
