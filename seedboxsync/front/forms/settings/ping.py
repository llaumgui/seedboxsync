#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync WTForms form for settings ping services."""

from flask_wtf import FlaskForm
from wtforms import BooleanField, URLField
from seedboxsync.front.babel import gettext as _


class SettingsPingForm(FlaskForm):  # type: ignore[misc]
    """
    Form for configuring external ping and health check services.

    Manages enablement toggles and webhook target URLs for monitoring
    background synchronization tasks via external services (e.g., Healthchecks.io).
    """

    healthchecks_sync_blackhole_enabled = BooleanField(_("Enable for sync_blackhole task?"))
    healthchecks_sync_blackhole_ping_url = URLField(
        _("Ping URL for sync_blackhole task"), render_kw={"placeholder": "https://hc-ping.com/94db845e-bd7c-42af-9ca8-25e89556b814", "icon": "fa-globe"}
    )
    healthchecks_sync_seedbox_enabled = BooleanField(_("Enable for sync_seedbox task?"))
    healthchecks_sync_seedbox_ping_url = URLField(
        _("Ping URL for sync_seedbox task"), render_kw={"placeholder": "https://hc-ping.com/826cb034-14fe-4965-a9d9-bc0bed7b034d", "icon": "fa-globe"}
    )
