#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Callback for tracking and persisting download progress."""

from seedboxsync.core import current_app
from seedboxsync.core.dao import Download
from seedboxsync.core.taskmanager.track_taskstatus import heartbeat


class DownloadProgress:
    """Track download progress and update its database record."""

    def __init__(self, download: Download) -> None:
        """
        Initialize the download progress tracker.

        Args:
            download: The download record to update.
        """
        self.app = current_app
        self._download = download
        self._last_saved_size = 0

    def __call__(self, transferred: int, total: int) -> None:
        """
        Update the download progress and persist it when appropriate.

        Args:
            transferred: Number of bytes transferred so far.
            total: Total number of bytes to transfer.
        """
        # Persist progress every 100 MiB and when the download completes.
        if transferred == total or transferred - self._last_saved_size >= 100 * 1024 * 1024:
            heartbeat()  # Call heartbeat
            self._download.local_size = transferred
            percent = (transferred / total) * 100 if total > 0 else 0
            self.app.logger.debug(f"Download progress: {transferred} / {total} ({percent:.2f}%)")
            self._download.save()
            self._last_saved_size = transferred
