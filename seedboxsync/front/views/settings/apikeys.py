#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for settings ApiKeys."""

from typing import cast
from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user
from werkzeug.wrappers.response import Response
from seedboxsync.core import current_app
from seedboxsync.core.database.models import ApiKey, User
from seedboxsync.front.babel import gettext as _
from seedboxsync.front.forms import ApiKeyForm, EmptyCSRFForm
from seedboxsync.front.login_manager import login_required
from seedboxsync.front.utils import toast
from seedboxsync.front.views import bp_settings as bp


@bp.route("/apikeys", methods=["GET"])
@login_required  # type: ignore[untyped-decorator]
def apikeys() -> str | Response:
    """
    Render the API keys management page and handle key creation.

    Displays active API keys for the currently authenticated user and handles
    generating new keys upon valid form submission.

    Returns:
        str | Response: Rendered HTML template containing the user's API keys list.
    """
    apikeys: list[ApiKey] = []
    if current_user.is_authenticated:
        apikeys = list(ApiKey.select(ApiKey.id, ApiKey.name, ApiKey.created, ApiKey.last_used))

    return render_template("settings/apikeys.html", apikeys=apikeys)


@bp.route("/apikeys/create", methods=["GET", "POST"])
@login_required  # type: ignore[untyped-decorator]
def apikeys_create() -> str | Response:
    """
    Render and process the user creation view.

    Handles fetching user data, populating the creation form, verifying password
    confirmations, hashing new passwords, and saving updates to the database.

    Returns:
        str | Response: Rendered HTML edit form template.
    """
    form = ApiKeyForm()
    if form.validate_on_submit():
        try:
            apikey = ApiKey()
            apikey_name = form.name.data or ""
            user_instance = cast(User, current_user)
            _apikey, apikey_raw = apikey.generate(user_instance, name=apikey_name)
            toast(_("API key created successfully."), _("API key"), "success")
            flash(
                _("API key '%(apikey_name)s' created successfully. Copy it now, as it will not be displayed again: '%(apikey_raw)s'")
                % {"apikey_name": apikey_name, "apikey_raw": apikey_raw},
                "info",
            )
            return redirect(url_for("settings.apikeys"))
        except Exception as e:
            current_app.logger.exception("Failed to save apikey.", exc_info=e)
            toast(_("Failed to save apikey."), _("API key"), "danger")
    return render_template("settings/apikeys_create.html", form=form)


@bp.route("/apikeys/<int:apikey_id>/delete", methods=["GET", "POST"])
@login_required  # type: ignore[untyped-decorator]
def apikeys_delete(apikey_id: int) -> str | Response:
    """
    Render and process the apikey delete view.

    Handles fetching apikey data, populating the delete form, verifying password
    confirmations, hashing new passwords, and saving updates to the database.

    Args:
        apikey_id (int): Database identifier of the apikey to edit.

    Returns:
        str | Response: Rendered HTML edit form template.

    Raises:
        HTTPException: 404 error if no apikey matches the given ID.
    """
    form = EmptyCSRFForm()
    try:
        apikey = ApiKey.get(ApiKey.id == apikey_id)
    except ApiKey.DoesNotExist:  # type: ignore[attr-defined]
        abort(404, f"API key id {apikey_id} doesn't exist.")

    if form.validate_on_submit():
        try:
            apikey_name = apikey.name
            apikey.delete_instance()
            toast(_("API key '%(apikey_name)s' deleted successfully.") % {"apikey_name": apikey_name}, _("API key"), "success")
            return redirect(url_for("settings.apikeys"))
        except Exception as e:
            current_app.logger.exception("Failed to delete API key.", exc_info=e)
            toast(_("Failed to delete API key."), _("API key"), "danger")

    return render_template("settings/apikeys_delete.html", form=form, apikey=apikey)
