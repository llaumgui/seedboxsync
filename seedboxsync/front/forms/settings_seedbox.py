#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync WTForms form for settings Seedbox."""

from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, SelectField, StringField
from wtforms.validators import DataRequired, NumberRange, Regexp
from seedboxsync.front.babel import gettext as _
from seedboxsync.front.forms.validators import DomainOrIP


class SettingsSeedboxForm(FlaskForm):  # type: ignore[misc]
    """Form for settings Seedbox."""

    DOMAIN_REGEX = r"^(?:(?!-)[A-Za-z0-9-]{0,61}[A-Za-z0-9]\.)+[A-Za-z]{2,}$"
    OCTAL_REGEX = r"^(?:0|0o[0-7]{3,4})?$"

    seedbox_host = StringField(_("Hostname"), validators=[DataRequired(), DomainOrIP()], render_kw={"placeholder": "my-seedbox.ltd", "icon": "fa-server"})
    seedbox_port = IntegerField(_("Port"), validators=[DataRequired(), NumberRange(min=1, max=65535)], render_kw={"placeholder": "22", "icon": "fa-plug"})
    seedbox_login = StringField(_("Login"), validators=[DataRequired()], render_kw={"placeholder": "me", "icon": "fa-user"})
    seedbox_password = PasswordField(_("Password"), validators=[DataRequired()], render_kw={"placeholder": "********", "icon": "fa-key"})
    seedbox_timeout = IntegerField(_("Timeout (in seconds)"), validators=[NumberRange(min=0, max=100000)], render_kw={"placeholder": "30", "icon": "fa-clock"})
    seedbox_protocol = SelectField(
        _("Protocol"),
        choices=[
            ("sftp", _("sFTP")),
            ("ftp", _("FTP")),
        ],
        default="sftp",
    )
    seedbox_chmod = StringField(
        _("chmod (in octal notation)"),
        validators=[Regexp(OCTAL_REGEX)],
        render_kw={"placeholder": "0o644", "icon": "fa-lock", "help": _("Chmod torrent after upload. Use octal notation, e.g. 0o644.")},
    )
    seedbox_max_concurrent_prefetch_requests = IntegerField(
        _("Max concurrent prefetch requests"),
        validators=[DataRequired(), NumberRange(min=1, max=1024)],
        render_kw={
            "placeholder": "128",
            "icon": "fa-check",
            "help": (
                _(
                    "Only for SFTP (Paramiko). The maximum number of concurrent read requests to prefetch. When this is None (the default), do not limit "
                    "the number of concurrent prefetch requests."
                    "Note: OpenSSH's sftp internally imposes a limit of 64 concurrent requests, while Paramiko imposes no limit by default; consider setting "
                    "a limit if a file can be successfully received with sftp but hangs with Paramiko."
                )
            ),
        },
    )
    seedbox_tmp_path = StringField(
        _("Tempory path"),
        validators=[DataRequired()],
        render_kw={"placeholder": "./tmp", "icon": "fa-folder", "help": _("Use a temporary directory for incomplete transfers (must be created manually).")},
    )
    seedbox_watch_path = StringField(
        _("Watch path"),
        validators=[DataRequired()],
        render_kw={"placeholder": "./watch", "icon": "fa-folder", "help": _("Your BitTorrent client's watch folder (must be created manually).")},
    )
    seedbox_finished_path = StringField(
        _("Finished path"),
        validators=[DataRequired()],
        render_kw={"placeholder": "./downdloads", "icon": "fa-folder", "help": _("The folder where your BitTorrent client puts finished files.")},
    )
    seedbox_prefixed_path = StringField(
        _("Prefixed path"),
        render_kw={"placeholder": "dowloaded", "icon": "fa-broom", "help": _("Remove a prefix from the synced path (usually the same as finished_path).")},
    )
    seedbox_part_suffix = StringField(
        _("Suffix used for .part"),
        render_kw={"placeholder": ".part", "icon": "fa-caret-left", "help": _("Exclude files with this suffix (e.g. incomplete downloads).")},
    )
    seedbox_exclude_syncing = StringField(
        _("Files to exclude from synching"),
        render_kw={
            "placeholder": "^.*missing$",
            "icon": "fa-ban",
            "help": _("Exclude files from sync using a regular expression (Python re syntax). Example: .*missing$"),
        },
    )
