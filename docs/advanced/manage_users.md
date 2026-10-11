---
title: Manage users
summary: Manage users from comand line
---

# Manage users from the command line

You can manage user accounts directly from the SeedboxSync command-line interface.

## Add a user

* Run the `user add` command without parameters to launch an interactive prompt to create a new user:

```bash
$ seedboxsync user add
Username: test
Email address: test@test.com
Password:
Repeat for confirmation:
Grant admin privileges? [y/N]: N
User 'test' (ID: 6) created successfully.
```

* Afterward, you can list users to verify the newly created account:

```bash
$ seedboxsync user list
┏━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Id ┃ Username ┃ Email                   ┃ Origin ┃ Is Admin ┃ Created             ┃ Last Login          ┃
┡━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 2  │ admin    │ admin@admin.ltd         │ local  │ True     │ 2026-09-11 09:37:24 │ 2026-10-10 17:01:13 │
│ 6  │ test     │ test@test.com           │ local  │ False    │ 2026-10-11 11:32:31 │ None                │
└────┴──────────┴─────────────────────────┴────────┴──────────┴─────────────────────┴─────────────────────┘
```

## Edit user details (e.g., reset password)

You can update user attributes such as username, email, or password using the `user edit` command:

```bash
$ seedboxsync user edit --id 6 --password mysecretpassword
User 'test' (ID: 6) updated successfully.
```

## Grant or revoke admin privileges

You can manage administrative rights using the `--is-admin` or `--no-is-admin` flags:

```bash
$ seedboxsync user edit --id 6 --is-admin
User 'test' (ID: 6) updated successfully.

$ seedboxsync user list
┏━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Id ┃ Username ┃ Email                   ┃ Origin ┃ Is Admin ┃ Created             ┃ Last Login          ┃
┡━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 2  │ admin    │ admin@admin.ltd         │ local  │ True     │ 2026-09-11 09:37:24 │ 2026-10-10 17:01:13 │
│ 6  │ test     │ test@test.com           │ local  │ True     │ 2026-10-11 11:32:31 │ None                │
└────┴──────────┴─────────────────────────┴────────┴──────────┴─────────────────────┴─────────────────────┘
```

To revoke admin privileges later, use `--no-is-admin`:

```bash
$ seedboxsync user edit --id 6 --no-is-admin
User 'test' (ID: 6) updated successfully.

$ seedboxsync user list
┏━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Id ┃ Username ┃ Email                   ┃ Origin ┃ Is Admin ┃ Created             ┃ Last Login          ┃
┡━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 2  │ admin    │ admin@admin.ltd         │ local  │ True     │ 2026-09-11 09:37:24 │ 2026-10-10 17:01:13 │
│ 6  │ test     │ test@test.com           │ local  │ False    │ 2026-10-11 11:32:31 │ None                │
└────┴──────────┴─────────────────────────┴────────┴──────────┴─────────────────────┴─────────────────────┘
```

## Delete a user

To remove a user account by its ID, use the `user delete` command:

```bash
$ seedboxsync user delete  --id 6
Are you sure you want to delete user 'test' (ID: 6)? [y/N]: y
User 'test' (ID: 6) deleted successfully.
```
