#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync WTForms dummy form for CSRF validation."""

from flask_wtf import FlaskForm


class EmptyCSRFForm(FlaskForm):  # type: ignore[misc]
    """
    Empty WTForms form used exclusively for validating CSRF tokens.

    Serves as a lightweight form wrapper when performing non-data POST actions
    (such as deletions or state toggles) to ensure CSRF protection.
    """
