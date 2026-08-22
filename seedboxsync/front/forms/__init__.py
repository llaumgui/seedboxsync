#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Form package with all forms."""

from .login import LoginForm
from .settings_nas import SettingsNasForm
from .settings_ping import SettingsPingForm
from .settings_seedbox import SettingsSeedboxForm
from .settings_seedboxsync import SettingsSeedboxSyncForm

__all__ = ["LoginForm", "SettingsNasForm", "SettingsPingForm", "SettingsSeedboxForm", "SettingsSeedboxSyncForm"]
