import pytest

from seedboxsync.cli import cli
from seedboxsync.core.dao import Download


@pytest.fixture
def stats_data(app):
    with app.app_context():
        Download.delete().execute()
        Download.create(path="one", seedbox_size=1024, local_size=1024, finished="2025-01-10")
        Download.create(path="two", seedbox_size=2048, local_size=2048, finished="2025-01-20")
        Download.create(path="three", seedbox_size=4096, local_size=4096, finished="2026-02-01")
        Download.create(path="active", seedbox_size=8192, local_size=1, finished=0)


def test_stats_without_subcommand_shows_help_and_totals(stats_data, runner):
    result = runner.invoke(cli, ["stats"])

    assert result.exit_code == 0
    assert "Commands:" in result.output
    assert "Nb files" in result.output
    assert "|          3 | 7.0 KiB" in result.output


def test_stats_total_ignores_unfinished_downloads(stats_data, runner):
    result = runner.invoke(cli, ["stats", "total"])

    assert result.exit_code == 0
    assert "|          3 | 7.0 KiB" in result.output


def test_stats_by_month_aggregates_files_and_sizes(stats_data, runner):
    result = runner.invoke(cli, ["stats", "by-month"])

    assert result.exit_code == 0
    assert "2025-01" in result.output
    assert "3.0 KiB" in result.output
    assert "2026-02" in result.output
    assert "4.0 KiB" in result.output
    assert "active" not in result.output


def test_stats_by_year_aggregates_files_and_sizes(stats_data, runner):
    result = runner.invoke(cli, ["stats", "by-year"])

    assert result.exit_code == 0
    assert "|   2025 |          2 | 3.0 KiB" in result.output
    assert "|   2026 |          1 | 4.0 KiB" in result.output
