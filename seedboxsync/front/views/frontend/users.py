#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for users management."""

from flask import abort, flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash
from werkzeug.wrappers.response import Response
from seedboxsync.core import current_app as app
from seedboxsync.core.dao import User
from seedboxsync.front.babel import gettext as _
from seedboxsync.front.forms import EmptyCSRFForm, UserForm
from seedboxsync.front.login_manager import login_required
from seedboxsync.front.views import bp_frontend as bp

settings_users_url = "frontend.settings_users"
msg_logger_error = "Failed to save user."
msg_flash_error = _("Failed to save user.")
msg_flash_success = _("User saved successfully.")


@bp.route("/settings/users")
@login_required  # type: ignore[untyped-decorator]
def settings_users() -> str | Response:
    """
    Render the users management settings page.

    Retrieves all registered users with their core metadata to display
    in the administrative user table.

    Returns:
        str | Response: Rendered HTML template containing the users list.
    """
    users = User.select(User.id, User.username, User.email, User.created, User.last_login)

    return render_template("settings/users.html", users=users)


@bp.route("/settings/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required  # type: ignore[untyped-decorator]
def settings_users_edit(user_id: int) -> str | Response:
    """
    Render and process the user edition view.

    Handles fetching user data, populating the edition form, verifying password
    confirmations, hashing new passwords, and saving updates to the database.

    Args:
        user_id (int): Database identifier of the user to edit.

    Returns:
        str | Response: Rendered HTML edit form template.

    Raises:
        HTTPException: 404 error if no user matches the given ID.
    """
    try:
        user = User.get(User.id == user_id)
    except User.DoesNotExist:  # pyright: ignore [reportAttributeAccessIssue]
        abort(404, f"User id {user_id} doesn't exist.")

    form = UserForm(obj=user)
    if form.validate_on_submit():
        # Check password 1 et 2
        password2 = request.form.get("password2", "")
        if form.password.data != password2:
            form.password.errors.append(_("Passwords do not match."))  # pyright: ignore [reportAttributeAccessIssue]
        else:
            try:
                form.populate_obj(user)
                if form.password.data:
                    user.password = generate_password_hash(form.password.data)
                user.save()
                flash(msg_flash_success, "success")
                return redirect(url_for(settings_users_url))
            except Exception as e:
                app.logger.exception(msg_logger_error, exc_info=e)
                flash(msg_flash_error, "danger")

    return render_template("settings/users_edit.html", form=form, action=_("User add"))


@bp.route("/settings/users/<int:user_id>/delete", methods=["GET", "POST"])
@login_required  # type: ignore[untyped-decorator]
def settings_users_delete(user_id: int) -> str | Response:
    """
    Render and process the user delete view.

    Handles fetching user data, populating the delete form, verifying password
    confirmations, hashing new passwords, and saving updates to the database.

    Args:
        user_id (int): Database identifier of the user to edit.

    Returns:
        str | Response: Rendered HTML edit form template.

    Raises:
        HTTPException: 404 error if no user matches the given ID.
    """
    form = EmptyCSRFForm()
    try:
        user = User.get(User.id == user_id)
    except User.DoesNotExist:  # pyright: ignore [reportAttributeAccessIssue]
        abort(404, f"User id {user_id} doesn't exist.")

    if form.validate_on_submit():
        try:
            username = user.username
            user.delete_instance()
            flash(_("User '%(username)s' deleted successfully.") % {"username": username}, "success")
            return redirect(url_for(settings_users_url))
        except Exception as e:
            app.logger.exception(msg_logger_error, exc_info=e)
            flash(_("Failed to delete user."), "danger")

    return render_template("settings/users_delete.html", form=form, user=user, action=_("User delete"))


@bp.route("/settings/users/create", methods=["GET", "POST"])
@login_required  # type: ignore[untyped-decorator]
def settings_users_create() -> str | Response:
    """
    Render and process the user creation view.

    Handles fetching user data, populating the creation form, verifying password
    confirmations, hashing new passwords, and saving updates to the database.

    Returns:
        str | Response: Rendered HTML edit form template.
    """
    form = UserForm()
    if form.validate_on_submit():
        # Check password 1 et 2
        password2 = request.form.get("password2", "")
        if form.password.data != password2:
            form.password.errors.append(_("Passwords do not match."))  # pyright: ignore [reportAttributeAccessIssue]
        else:
            try:
                user = User()
                form.populate_obj(user)
                if form.password.data:
                    user.password = generate_password_hash(form.password.data)
                user.save()
                flash(msg_flash_success, "success")
                return redirect(url_for(settings_users_url))
            except Exception as e:
                app.logger.exception(msg_logger_error, exc_info=e)
                flash(msg_flash_error, "danger")

    return render_template("settings/users_edit.html", form=form, action=_("User add"))
