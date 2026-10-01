import datetime
from unittest.mock import patch
from seedboxsync.core.database.models import Download


def test_set_mime_updates_fields_and_optionally_saves(app):
    with app.app_context():
        download = Download.create(path="/downloads/video", seedbox_size=100)
        mime_result = ("video/mp4", ".mp4", "magic")

        with patch("seedboxsync.core.database.models.download.utils.get_mime_type_from_file", return_value=mime_result):
            download.set_mime()

        assert (download.mime_type, download.mime_extension, download.mime_confidence) == mime_result

        with (
            patch("seedboxsync.core.database.models.download.utils.get_mime_type_from_file", return_value=mime_result),
            patch.object(download, "save", wraps=download.save) as save,
        ):
            download.set_mime(save=True)

        save.assert_called_once_with()


def test_is_already_download_requires_a_finished_record(app):
    with app.app_context():
        Download.delete().execute()
        Download.create(path="/downloads/pending", seedbox_size=10, finished=0)
        Download.create(path="/downloads/complete", seedbox_size=20, finished=datetime.datetime.now())

        assert not Download.is_already_download("/downloads/pending")
        assert Download.is_already_download("/downloads/complete")
        assert not Download.is_already_download("/downloads/missing")


def test_get_stats_by_mime_type_filters_and_orders_results(app):
    with app.app_context():
        Download.delete().execute()
        Download.create(
            path="/downloads/small.mp4",
            seedbox_size=100,
            local_size=100,
            mime_type="video/mp4",
            finished=datetime.datetime(2025, 1, 2),
        )
        Download.create(
            path="/downloads/large.mp4",
            seedbox_size=300,
            local_size=300,
            mime_type="video/mp4",
            finished=datetime.datetime(2025, 1, 3),
        )
        Download.create(
            path="/downloads/image.png",
            seedbox_size=200,
            local_size=200,
            mime_type="image/png",
            finished=datetime.datetime(2025, 1, 2),
        )

        all_stats = Download.get_stats_by_mime_type()
        filtered_stats = Download.get_stats_by_mime_type(start_date=datetime.date(2025, 1, 3))
        end_filtered_stats = Download.get_stats_by_mime_type(end_date=datetime.date(2025, 1, 4))

    assert [row["mime_type"] for row in all_stats] == ["video/mp4", "image/png"]
    assert all_stats[0]["total"] == 2
    assert all_stats[0]["total_size"] == 400
    assert [row["mime_type"] for row in filtered_stats] == ["video/mp4"]
    assert filtered_stats[0]["total"] == 1
    assert end_filtered_stats == all_stats


def test_get_stats_handles_empty_and_populated_periods(app):
    with app.app_context():
        Download.delete().execute()
        empty_stats = Download.get_stats()
        now = datetime.datetime.now()
        Download.create(path="/downloads/today", seedbox_size=100, local_size=100, finished=now)
        Download.create(path="/downloads/yesterday", seedbox_size=200, local_size=200, finished=now - datetime.timedelta(days=1))
        populated_stats = Download.get_stats()

    assert set(empty_stats) == {"day", "week", "month", "year", "last24h", "last7d", "last30d"}
    assert all(stats["total"] == 0 and stats["trend_total"] == "0.0%" for stats in empty_stats.values())
    assert populated_stats["day"]["total"] == 1
    assert populated_stats["day"]["trend_total"] == "+0.0%"
    assert populated_stats["last7d"]["trend_size"] == "+∞%"
