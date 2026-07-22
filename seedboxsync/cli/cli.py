#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Cli module."""

from importlib import import_module
from pathlib import Path
from typing import Any, ClassVar, cast
import click
from flask.cli import FlaskGroup
from seedboxsync.cli.context import Context


def pass_context(func: Any) -> Any:
    """
    Decorate a callback to receive the custom SeedboxSync Click context.

    Args:
        func: The callback to decorate.

    Returns:
        The decorated callback.
    """
    return click.pass_context(func)


class Cli(FlaskGroup):
    """
    SeedboxSync command-line interface.

    This class customizes Flask's default CLI by:
    - using the SeedboxSync context implementation;
    - hiding Flask-specific global options;
    - automatically loading commands from the ``commands`` package;
    - using custom command and group classes by default.
    """

    context_class = Context
    _CMD_FOLDER = Path(__file__).resolve().parent / "commands"
    _HIDDEN_FLASK_OPTIONS: ClassVar[frozenset[str]] = frozenset(
        {
            "--app",
            "-A",
            "--env-file",
            "-e",
        }
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the CLI and remove Flask-specific global options.

        Args:
            *args (Any): Positional arguments forwarded to ``FlaskGroup``.
            **kwargs (Any): Keyword arguments forwarded to ``FlaskGroup``.
        """
        super().__init__(*args, **kwargs)

        self.params = [parameter for parameter in self.params if not self._is_hidden_flask_option(parameter)]

    def _is_hidden_flask_option(self, parameter: click.Parameter) -> bool:
        """
        Determine whether a Click parameter is a hidden Flask option.

        Args:
            parameter (click.Parameter): The Click parameter to inspect.

        Returns:
            ``True`` if the parameter should be hidden, otherwise ``False``.
        """
        if not isinstance(parameter, click.Option):
            return False

        option_names = set(parameter.opts) | set(parameter.secondary_opts)

        return bool(option_names & self._HIDDEN_FLASK_OPTIONS)

    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        """
        Parse command-line arguments without Flask's implicit global options.

        Args:
            ctx (click.Context,): The Click context.
            args (list): The command-line arguments.

        Returns:
            The parsed arguments.
        """
        return click.Group.parse_args(self, ctx, args)

    def command(self, *args: Any, **kwargs: Any) -> Any:
        """
        Create a command using the custom SeedboxSync command class.

        Args:
            *args (Any): Positional arguments forwarded to Click.
            **kwargs (Any): Keyword arguments forwarded to Click.

        Returns:
            The decorated command.
        """
        kwargs.setdefault("cls", Command)
        return super().command(*args, **kwargs)

    def group(self, *args: Any, **kwargs: Any) -> Any:
        """
        Create a group using the custom SeedboxSync group class.

        Args:
            *args (Any): Positional arguments forwarded to Click.
            **kwargs (Any): Keyword arguments forwarded to Click.

        Returns:
            The decorated group.
        """
        kwargs.setdefault("cls", Group)
        return super().group(*args, **kwargs)

    def list_commands(self, ctx: click.Context) -> list[str]:
        """
        Return the list of available SeedboxSync commands.

        Args:
            ctx (click.Context): The Click context.

        Returns:
            A sorted list of available command names.
        """
        rv = []

        for path in self._CMD_FOLDER.iterdir():
            if path.is_file() and path.suffix == ".py" and path.stem.startswith("cmd_"):
                rv.append(path.stem[4:])

        rv.sort()
        return rv

    def get_command(self, ctx: click.Context, name: str) -> click.Command | None:
        """
        Load a command module dynamically.

        Args:
            ctx (click.Context): The Click context.
            name (str): The command name.

        Returns:
            The loaded Click command, or ``None`` if the command cannot be loaded.
        """
        try:
            mod = import_module(f"seedboxsync.cli.commands.cmd_{name}")
        except ImportError as e:
            click.echo(e, err=True)
            click.echo(f"Command '{name}' not found.", err=True)
            return None
        return cast(click.Command, mod.cli)

    def invoke(self, ctx: click.Context) -> Any:
        """
        Invoke the selected command and handle user interruptions gracefully.

        Args:
            ctx (click.Context): The Click context.

        Returns:
            The command result.
        """
        try:
            return super().invoke(ctx)
        except KeyboardInterrupt as exc:
            click.secho("\nInterrupted by user.", fg="yellow")
            raise ctx.exit(130) from exc


class Command(click.Command):
    """SeedboxSync Click command using the custom context implementation."""

    context_class = Context


class Group(click.Group):
    """SeedboxSync Click command group using the custom context implementation."""

    context_class = Context

    def command(self, *args: Any, **kwargs: Any) -> Any:
        """
        Create a command using the SeedboxSync command class by default.

        Args:
            *args (Any): Positional arguments forwarded to Click.
            **kwargs (Any): Keyword arguments forwarded to Click.

        Returns:
            The decorated command.
        """
        kwargs.setdefault("cls", Command)
        return super().command(*args, **kwargs)

    def group(self, *args: Any, **kwargs: Any) -> Any:
        """
        Create a group using the SeedboxSync group class by default.

        Args:
            *args (Any): Positional arguments forwarded to Click.
            **kwargs (Any): Keyword arguments forwarded to Click.

        Returns:
            The decorated group.
        """
        kwargs.setdefault("cls", Group)
        return super().group(*args, **kwargs)


def command(*args: Any, **kwargs: Any) -> Any:
    """
    Create a Click command using the SeedboxSync command class.

    Args:
        *args (Any): Positional arguments forwarded to Click.
        **kwargs (Any): Keyword arguments forwarded to Click.

    Returns:
        The decorated command.
    """
    kwargs.setdefault("cls", Command)
    return click.command(*args, **kwargs)


def group(*args: Any, **kwargs: Any) -> Any:
    """
    Create a Click group using the SeedboxSync group class.

    Args:
        *args (Any): Positional arguments forwarded to Click.
        **kwargs (Any): Keyword arguments forwarded to Click.

    Returns:
        The decorated group.
    """
    kwargs.setdefault("cls", Group)
    return click.group(*args, **kwargs)
