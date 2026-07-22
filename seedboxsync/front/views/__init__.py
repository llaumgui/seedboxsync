#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Package "view" initialization."""

import importlib
import pkgutil
from flask import Blueprint

bp = Blueprint("frontend", __name__)


def _load_controllers() -> None:
    """Load compliant with mypy..."""
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{module_name}")


_load_controllers()
