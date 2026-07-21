import logging
import pytest
import seedboxsync
from seedboxsync.cli import cli
from seedboxsync.core.db import Database


def test_help_lists_only_seedboxsync_options_and_commands(runner):
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Usage: seedboxsync [OPTIONS] COMMAND [ARGS]..." in result.output
    assert "--debug / --no-debug" in result.output
    assert "--app" not in result.output
    for command in ("clean", "search", "stats", "sync"):
        assert command in result.output


def test_no_command_displays_help(runner):
    result = runner.invoke(cli)

    # Click versions differ on whether implicit help is a successful exit or
    # a usage error. The stable CLI contract is that help is displayed.
    assert result.exit_code in (0, 2)
    assert "Usage: seedboxsync" in result.output
    if result.exit_code == 2:
        assert isinstance(result.exception, SystemExit)
    else:
        assert result.exception is None


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_help_aliases(runner, option):
    result = runner.invoke(cli, [option])

    assert result.exit_code == 0
    assert "Commands:" in result.output


def test_version_banner(runner):
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert f"SeedboxSync {seedboxsync.__version__}" in result.output
    assert f"SeedboxSync database {Database.DATABASE_VERSION}" in result.output


def test_debug_option_enables_debug_logging(app, runner):
    assert app.debug is False

    result = runner.invoke(cli, ["--debug", "stats", "total"])

    assert result.exit_code == 0
    assert app.debug is True
    assert app.logger.level == logging.DEBUG
