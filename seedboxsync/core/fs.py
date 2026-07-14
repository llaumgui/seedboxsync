# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
A collection of fs utility functions from Cement for SeedboxSync.
"""

import os
from typing import Any


def abspath(path: str, strip_trailing_slash: bool = True) -> str:
    """
    Return an absolute path, while also expanding the ``~`` user directory
    shortcut.

    Args:
        path (str): The original path to expand.

    Returns:
        str: The fully expanded, absolute path to the given ``path``

    Example:

        .. code-block:: python

            from seedboxsync.core.utils import fs

            fs.abspath('~/some/path')
            fs.abspath('./some.file')
    """
    return os.path.abspath(os.path.expanduser(path))


def ensure_dir_exists(path: str) -> None:
    """
    Ensure the directory ``path`` exists, and if not create it.

    Args:
        path (str): The filesystem path of a directory.

    Raises:
        AssertionError: If the directory ``path`` exists, but is not a
        directory.

    Returns: None
    """

    path = abspath(path)

    if os.path.exists(path) and not os.path.isdir(path):
        raise AssertionError(f"Path `{path}` exists but is not a directory!")
    elif not os.path.exists(path):
        os.makedirs(path)


def join(*args: str, **kwargs: Any) -> str:
    """
    Return a complete, joined path, by first calling ``abspath()`` on the first
    item to ensure the final path is complete.

    Args:
        paths (list): A list of paths to join together.

    Returns:
        list: The complete and absolute joined path.

    Example:

        .. code-block:: python

            from seedboxsync.core.utils import fs

            fs.join('~/some/path', 'some/other/relevant/paht')

    """
    paths = list(args)
    first_path = abspath(paths.pop(0))
    return os.path.join(first_path, *paths, **kwargs)
