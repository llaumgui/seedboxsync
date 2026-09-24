#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""All commands related to the users operations & management."""

import click
from peewee import fn
from werkzeug.security import generate_password_hash
from seedboxsync.cli import Context, group, pass_context
from seedboxsync.core.database.models import User


@group("user", help="User operations & management for SeedboxSync frontend.")  # type: ignore[untyped-decorator]
@pass_context
def cli(ctx: Context) -> None:
    """Empty function for Click sub commands."""


@cli.command("list", help="List users.")  # type: ignore[untyped-decorator]
@click.option("-n", "--number", type=int, default=10, help="Number of torrents to display.")
@click.option("-s", "--search", help="Term to search.")
@pass_context
def list_user(ctx: Context, number: int, search: str) -> None:
    """
    List registered users from the database.

    Queries user accounts with optional text filtering on usernames and renders
    a formatted table containing user metadata.

    Args:
        ctx (Context): The CLI application context.
        number (int): Maximum number of users to display. Defaults to 10.
        search (str): Optional search term to filter users by username.
    """
    # Build "where" expression
    conditions = []
    if search:
        conditions.append(User.username.contains(search))

    # DB query
    query = (
        User.select(
            User.id,
            User.username,
            User.email,
            User.origin,
            fn.short_datetime(User.created),
            fn.short_datetime(User.last_login),
        )
        .limit(number)
        .order_by(User.id.desc())
    )

    # if "where" expression
    if conditions:
        query = query.where(*conditions)
    data = query.dicts()

    click.echo(
        ctx.render(
            reversed(data),
            headers={"id": "Id", "username": "Username", "email": "Email", "origin": "Origin", "created": "Created", "last_login": "Last Login"},
        )
    )


@cli.command("delete", help="Delete a user.")  # type: ignore[untyped-decorator]
@click.option("--id", type=int, required=True, help="ID of the user to delete.")
@click.option("-y", "--yes", is_flag=True, help="Confirm deletion without prompting.")
@pass_context
def delete(ctx: Context, id: int, yes: bool) -> None:  # noqa: A002
    """
    Delete a user by their unique database identifier.

    Args:
        ctx (Context): The CLI application context.
        id (int): Database identifier of the user to remove.
        yes (bool): Skip confirmation prompt if set to True.
    """
    try:
        user = User.get_by_id(id)
    except User.DoesNotExist:  # pyright: ignore [reportAttributeAccessIssue]
        click.secho(f"Error: User with ID {id} does not exist.", fg="red", err=True)
        return

    if not yes and not click.confirm(f"Are you sure you want to delete user '{user.username}' (ID: {user.id})?"):
        click.echo("Operation canceled.")
        return

    try:
        username = user.username
        user.delete_instance()
        click.secho(f"User '{username}' (ID: {id}) deleted successfully.", fg="green")
    except Exception as e:
        click.secho(f"Error: Failed to delete user {id}: {e}", fg="red", err=True)


@cli.command("add", help="Add a new user.")  # type: ignore[untyped-decorator]
@click.option("-u", "--username", prompt="Username", help="Username for the new account.")
@click.option("-e", "--email", prompt="Email address", help="Unique email address.")
@click.option("-p", "--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Password for the user account.")
@pass_context
def add(ctx: Context, username: str, email: str, password: str) -> None:
    """
    Create a new user account in the database.

    Accepts account details via command-line options or interactive prompts,
    hashes the password, and stores the user record.

    Args:
        ctx (Context): The CLI application context.
        username (str): Unique username for the account.
        email (str): Unique email address.
        password (str): Plain-text password to hash and store.
    """
    # Verify if user already exists before attempting insertion
    if User.get_or_none((User.username == username) | (User.email == email)):
        click.secho(
            f"Error: A user with username '{username}' or email '{email}' already exists.",
            fg="red",
            err=True,
        )
        return

    try:
        user = User.create(
            username=username,
            email=email,
            password=generate_password_hash(password),
        )
        click.secho(f"User '{user.username}' (ID: {user.id}) created successfully.", fg="green")
    except Exception as e:
        click.secho(f"Error: Failed to create user: {e}", fg="red", err=True)


@cli.command("edit", help="Edit an existing user.")  # type: ignore[untyped-decorator]
@click.option("--id", type=int, required=True, help="ID of the user to edit.")
@click.option("-u", "--username", help="New username for the account.")
@click.option("-e", "--email", help="New email address.")
@click.option("-p", "--password", help="New password for the account.")
@pass_context
def edit(ctx: Context, id: int, username: str | None, email: str | None, password: str | None) -> None:  # noqa: A002
    """
    Update details for an existing user account.

    Fetches the user by ID and updates only the provided fields. Password
    updates are automatically hashed before saving.

    Args:
        ctx (Context): The CLI application context.
        id (int): Database identifier of the user to edit.
        username (str | None): New username to set.
        email (str | None): New email address to set.
        password (str | None): New plain-text password to hash and update.
    """
    try:
        user = User.get_by_id(id)
    except User.DoesNotExist:  # pyright: ignore [reportAttributeAccessIssue]
        click.secho(f"Error: User with ID {id} does not exist.", fg="red", err=True)
        return

    # Check unique constraint collisions if username or email is being updated
    if username and username != user.username:
        if User.get_or_none(User.username == username):
            click.secho(f"Error: Username '{username}' is already taken.", fg="red", err=True)
            return
        user.username = username

    if email and email != user.email:
        if User.get_or_none(User.email == email):
            click.secho(f"Error: Email '{email}' is already taken.", fg="red", err=True)
            return
        user.email = email

    if password:
        user.password = generate_password_hash(password)

    try:
        user.save()
        click.secho(f"User '{user.username}' (ID: {user.id}) updated successfully.", fg="green")
    except Exception as e:
        click.secho(f"Error: Failed to update user {id}: {e}", fg="red", err=True)
