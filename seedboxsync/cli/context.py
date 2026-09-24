#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Build a context used by Click."""

from collections.abc import Iterable
from functools import cached_property
from typing import Any, Literal, TypedDict
import click
from rich.console import Console
from rich.table import Table
from seedboxsync.core import Flask, current_app


class HeaderOptions(TypedDict, total=False):
    """Rich table column options."""

    title: str
    justify: Literal["default", "left", "center", "right", "full"]
    style: str
    no_wrap: bool
    overflow: Literal["fold", "crop", "ellipsis", "ignore"]
    width: int
    min_width: int
    max_width: int
    ratio: int


Header = str | HeaderOptions
Headers = dict[str, Header]


class Context(click.Context):
    """SeedboxSync Click context."""

    @cached_property
    def app(self) -> Flask:
        """
        Return the current Flask application.

        Returns:
            Flask: The current Flask application.
        """
        return current_app

    def render(self, data: Iterable[Any], headers: Headers, title: str | None = None) -> str:
        """
        Render tabular data as a Rich table.

        Args:
            data: Tabular data to render.
            headers: Column headers.
            title: Table title.

        Returns:
            str: The formatted table..
        """
        console = Console()
        table = Table(title=title)

        # Set columns from headers
        for key, header in headers.items():
            if isinstance(header, str):
                column_title = header
                table.add_column(column_title)
                continue

            column_title = header.get("title", key)

            table.add_column(
                column_title,
                justify=header.get("justify", "left"),
                style=header.get("style"),
                no_wrap=header.get("no_wrap", False),
                overflow=header.get("overflow", "ellipsis"),
                width=header.get("width"),
                min_width=header.get("min_width"),
                max_width=header.get("max_width"),
                ratio=header.get("ratio"),
            )

        # Set rows from headers and data
        for row in data:
            table.add_row(*(str(row.get(column, "")) for column in headers))

        # Return as string
        with console.capture() as capture:
            console.print(table)
        return capture.get()
