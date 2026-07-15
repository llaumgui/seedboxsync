from seedboxsync.cli import cli
from seedboxsync.core.dao import Download


def test_clean_progress_deletes_only_unfinished_downloads(app, runner):
    with app.app_context():
        unfinished_before = Download.select().where(Download.finished == 0).count()
        finished_before = Download.select().where(Download.finished != 0).count()

    result = runner.invoke(cli, ["clean", "progress"])

    assert result.exit_code == 0
    assert result.output == f"In progress list cleaned. {unfinished_before} line(s) deleted\n"
    with app.app_context():
        assert Download.select().where(Download.finished == 0).count() == 0
        assert Download.select().where(Download.finished != 0).count() == finished_before


def test_clean_downloaded_requires_an_integer_id(runner):
    missing = runner.invoke(cli, ["clean", "downloaded"])
    invalid = runner.invoke(cli, ["clean", "downloaded", "not-an-id"])

    assert missing.exit_code == 2
    assert "Missing argument 'ID'" in missing.output
    assert invalid.exit_code == 2
    assert "not a valid integer" in invalid.output


def test_clean_downloaded_removes_the_selected_row(app, runner):
    with app.app_context():
        download = Download.create(path="remove-me", seedbox_size=12, local_size=12, finished="2026-01-01 00:00:00")
        download_id = download.id

    result = runner.invoke(cli, ["clean", "downloaded", str(download_id)])

    assert result.exit_code == 0
    assert result.output == f"Torrent with id {download_id} was removed\n"
    with app.app_context():
        assert Download.get_or_none(Download.id == download_id) is None


def test_clean_downloaded_reports_unknown_id(runner):
    result = runner.invoke(cli, ["clean", "downloaded", "999999"])

    assert result.exit_code == 0
    assert result.output == "No downloaded file with id 999999\n"
