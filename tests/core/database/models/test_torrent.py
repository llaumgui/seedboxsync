from types import SimpleNamespace
from unittest.mock import patch
from seedboxsync.core.database.models import Torrent


def test_set_from_file_rejects_invalid_data_and_accepts_missing_info():
    torrent = Torrent(name="example")

    with patch("seedboxsync.core.database.models.torrent.utils.get_torrent_infos", return_value=None):
        assert not torrent.set_from_file("invalid.torrent")

    with patch("seedboxsync.core.database.models.torrent.utils.get_torrent_infos", return_value={"announce": "https://tracker.example/announce"}):
        assert torrent.set_from_file("minimal.torrent")

    assert torrent.announce == "https://tracker.example/announce"
    assert torrent.total_files is None
    assert torrent.total_size is None


def test_set_from_file_extracts_single_file_metadata():
    torrent = Torrent(name="single")
    torrent_info = {"announce": "", "info": {"source": "tracker", "private": True, "length": 1234}}

    with patch("seedboxsync.core.database.models.torrent.utils.get_torrent_infos", return_value=torrent_info):
        assert torrent.set_from_file("single.torrent")

    assert torrent.announce is None
    assert torrent.source == "tracker"
    assert torrent.private is True
    assert torrent.total_files == 1
    assert torrent.total_size == 1234


def test_set_from_file_counts_only_valid_multifile_entries():
    torrent = Torrent(name="multi")
    torrent_info = {"info": {"files": [{"length": 10}, {"length": "bad"}, None, {"length": 20}]}}

    with patch("seedboxsync.core.database.models.torrent.utils.get_torrent_infos", return_value=torrent_info):
        assert torrent.set_from_file("multi.torrent")

    assert torrent.total_files == 2
    assert torrent.total_size == 30
    assert torrent.private is False


def test_update_announcer_clears_missing_urls_and_falls_back_to_hostname():
    torrent = Torrent(name="example", announce=None)
    torrent.announcer = "old.example"
    torrent.update_announcer()
    assert torrent.announcer is None

    torrent.announce = "not a URL"
    torrent.update_announcer()
    assert torrent.announcer is None

    torrent.announce = "udp://tracker/announce"
    with patch("seedboxsync.core.database.models.torrent.tldextract.extract", return_value=SimpleNamespace(domain="", suffix="")):
        torrent.update_announcer()

    assert torrent.announcer == "tracker"


def test_save_sets_registrable_announcer_and_source(app):
    with app.app_context():
        extracted = SimpleNamespace(domain="example", suffix="org")
        with patch("seedboxsync.core.database.models.torrent.tldextract.extract", return_value=extracted):
            torrent = Torrent.create(name="example", announce="https://tracker.example.org/announce")

        assert torrent.announcer == "example.org"
        assert torrent.source == "example.org"


def test_get_stats_by_source_applies_date_filters(app):
    import datetime

    with app.app_context():
        Torrent.delete().execute()
        Torrent.create(name="old", source="old", total_size=100, sent=datetime.datetime(2025, 1, 1))
        Torrent.create(name="new", source="new", total_size=300, sent=datetime.datetime(2025, 1, 2))
        Torrent.create(name="later", source="later", total_size=500, sent=datetime.datetime(2025, 1, 4))

        stats = Torrent.get_stats_by_source(start_date=datetime.date(2025, 1, 2))
        end_filtered_stats = Torrent.get_stats_by_source(end_date=datetime.date(2025, 1, 3))

    assert {row["source"] for row in stats} == {"new", "later"}
    new_stats = next(row for row in stats if row["source"] == "new")
    assert new_stats["total"] == 1
    assert new_stats["total_size"] == 300
    assert {row["source"] for row in end_filtered_stats} == {"old", "new"}
