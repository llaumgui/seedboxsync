from unittest.mock import patch
import click
from seedboxsync.cli import cli
from seedboxsync.cli.cli import Cli, Command, Group
from seedboxsync.core.dao import SeedboxSync
from seedboxsync.core.db import Database


def test_test_database_is_migrated_when_app_is_created(app):
    with app.app_context():
        assert int(SeedboxSync.get_db_version()) == Database.DATABASE_VERSION


def test_cli_discovers_commands_dynamically(app):
    with app.test_request_context():
        context = click.Context(cli)
        assert cli.list_commands(context) == ["clean", "health", "search", "stats", "sync", "task"]


def test_cli_uses_custom_command_and_group_classes():
    root = Cli(name="test", create_app=lambda: None)

    @root.command("command")
    def sample_command():
        pass

    @root.group("group")
    def sample_group():
        pass

    assert isinstance(sample_command, Command)
    assert isinstance(sample_group, Group)


def test_unknown_command_returns_click_error(runner):
    result = runner.invoke(cli, ["unknown"])

    assert result.exit_code == 2
    assert "No such command 'unknown'" in result.output


def test_keyboard_interrupt_is_reported_with_shell_exit_code(runner):
    with patch("seedboxsync.cli.cli.FlaskGroup.invoke", side_effect=KeyboardInterrupt):
        result = runner.invoke(cli, ["stats"])

    assert result.exit_code == 130
    assert "Interrupted by user." in result.output
