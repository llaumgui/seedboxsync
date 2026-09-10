from unittest.mock import MagicMock, patch
from seedboxsync.core.sync.download_progress import DownloadProgress


def test_download_progress_saves_only_at_threshold_or_completion(app):
    download = MagicMock()

    with app.app_context(), patch("seedboxsync.core.sync.download_progress.heartbeat") as heartbeat:
        progress = DownloadProgress(download)
        progress(1024, 200 * 1024 * 1024)
        download.save.assert_not_called()

        progress(100 * 1024 * 1024, 200 * 1024 * 1024)
        assert download.local_size == 100 * 1024 * 1024
        download.save.assert_called_once_with()

        progress(200 * 1024 * 1024, 200 * 1024 * 1024)

    assert download.save.call_count == 2
    assert heartbeat.call_count == 2


def test_download_progress_handles_zero_length_completion(app):
    download = MagicMock()

    with app.app_context(), patch("seedboxsync.core.sync.download_progress.heartbeat") as heartbeat:
        DownloadProgress(download)(0, 0)

    assert download.local_size == 0
    download.save.assert_called_once_with()
    heartbeat.assert_called_once_with()
