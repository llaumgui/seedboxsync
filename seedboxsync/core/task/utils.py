# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
Task queue initialization and automatic task module registration.
"""

import importlib
import pkgutil
from types import ModuleType
from seedboxsync.core import current_app as app
import seedboxsync.core.task as task_package


def load_task_modules() -> list[ModuleType]:
    """
    Import all task modules from this package.

    Modules are loaded when their name starts with ``task_``. Importing them
    registers their decorated Huey tasks in the task queue registry.

    Returns:
        The list of imported task modules.
    """
    imported_modules: list[ModuleType] = []

    for module_info in pkgutil.iter_modules(task_package.__path__):
        if not module_info.name.startswith("task_"):
            continue

        module_name = f"{task_package.__name__}.{module_info.name}"
        app.logger.debug("Register task on %s", module_name)

        module = importlib.import_module(module_name)
        imported_modules.append(module)

    return imported_modules
