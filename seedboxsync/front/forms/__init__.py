#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Form package with all forms."""

from .csrf import EmptyCSRFForm
from .login import LoginForm
from .settings.authentication import SettingsAuthenticationForm
from .settings.nas import SettingsNasForm
from .settings.ping import SettingsPingForm
from .settings.seedbox import SettingsSeedboxForm
from .settings.seedboxsync import SettingsSeedboxSyncForm
from .user import UserForm

__all__ = [
    "EmptyCSRFForm",
    "LoginForm",
    "SettingsAuthenticationForm",
    "SettingsNasForm",
    "SettingsPingForm",
    "SettingsSeedboxForm",
    "SettingsSeedboxSyncForm",
    "UserForm",
]
