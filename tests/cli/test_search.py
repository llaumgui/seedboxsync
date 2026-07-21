import datetime
import pytest
from seedboxsync.cli import cli
from seedboxsync.core.dao import Download, Torrent


@pytest.fixture
def search_data(app):
    with app.app_context():
        Download.delete().execute()
        Torrent.delete().execute()
        Download.create(path="done-alpha.iso", seedbox_size=2048, local_size=2048, started="2026-01-01", finished="2026-01-02")
        Download.create(path="done-beta.iso", seedbox_size=4096, local_size=4096, started="2026-02-01", finished="2026-02-02")
        Download.create(path="active-alpha.iso", seedbox_size=1000, local_size=250, started=datetime.datetime.now(), finished=0)
        Torrent.create(name="alpha.torrent", sent="2026-01-01")
        Torrent.create(name="beta.torrent", sent="2026-02-01")


@pytest.mark.parametrize("subcommand", ["uploaded", "downloaded", "progress"])
def test_search_command_help(runner, subcommand):
    result = runner.invoke(cli, ["search", subcommand, "--help"])

    assert result.exit_code == 0
    assert "--number INTEGER" in result.output
    assert "--search TEXT" in result.output


def test_search_uploaded_filters_case_insensitively(search_data, runner):
    result = runner.invoke(cli, ["search", "uploaded", "--search", "ALPHA"])

    assert result.exit_code == 0
    assert "alpha.torrent" in result.output
    assert "beta.torrent" not in result.output
    assert "Sent datetime" in result.output


def test_search_uploaded_honors_result_limit(search_data, runner):
    result = runner.invoke(cli, ["search", "uploaded", "--number", "1"])

    assert result.exit_code == 0
    assert "beta.torrent" in result.output
    assert "alpha.torrent" not in result.output


def test_search_downloaded_excludes_active_rows(search_data, runner):
    result = runner.invoke(cli, ["search", "downloaded", "-s", "alpha"])

    assert result.exit_code == 0
    assert "done-alpha.iso" in result.output
    assert "active-alpha.iso" not in result.output
    assert "2.0 KiB" in result.output


def test_search_progress_only_lists_active_rows(search_data, runner):
    result = runner.invoke(cli, ["search", "progress", "-n", "1"])

    assert result.exit_code == 0
    assert "active-alpha.iso" in result.output
    assert "done-alpha.iso" not in result.output
    assert "25%" in result.output
    assert "Progress" in result.output


def test_search_rejects_invalid_number(search_data, runner):
    result = runner.invoke(cli, ["search", "uploaded", "--number", "many"])

    assert result.exit_code == 2
    assert "not a valid integer" in result.output
