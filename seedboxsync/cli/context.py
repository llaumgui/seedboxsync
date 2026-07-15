# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
Build a context used by Click.
"""

import click
from collections.abc import Iterable
from functools import cached_property
from typing import Any
from tabulate import tabulate
from seedboxsync.core import Flask, current_app
from seedboxsync.core.lock import Lock


class Context(click.Context):
    """
    SeedboxSync Click context.

    Args:
        ctx (click.Context): The Click context object.
    """

    @cached_property
    def app(self) -> Flask:
        """
        Return the current Flask application.

        Returns:
            Flask: The current Flask application.
        """
        return current_app

    @cached_property
    def lock(self) -> Lock:
        """
        Return a Lock instance.

        Returns:
            Lock: Lock instance.
        """
        return Lock()

    def render(self, data: Iterable[Any], headers: Iterable[Any], tablefmt: str = "github") -> Any:
        """
        Render tabular data using the specified output format.

        Args:
            data: Tabular data to render.
            headers: Column headers passed to ``tabulate``.
            tablefmt: Output table format.

        Returns:
            str: The formatted table.
        """
        return tabulate(data, headers=headers, tablefmt=tablefmt)
