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

bp_auth = Blueprint("auth", __name__)
bp_frontend = Blueprint("frontend", __name__)

SUB_PACKAGES = [
    "auth",
    "frontend",
]


def _load_views() -> None:
    """Dynamically import controller modules from sub-packages."""
    for subpackage in SUB_PACKAGES:
        # Import the sub-package itself first
        subpackage_pkg = importlib.import_module(f"{__name__}.{subpackage}")

        # Iterate over all modules inside the sub-package directory
        for _, module_name, is_pkg in pkgutil.iter_modules(subpackage_pkg.__path__):
            if not is_pkg:
                importlib.import_module(f"{__name__}.{subpackage}.{module_name}")


_load_views()
