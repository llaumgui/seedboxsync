---
title: Development Backend
summary: Development guide for SeedboxSync
---

This section covers development for the **SeedboxSync backend**.

## Tech Stack

* **Python 3**
* **[Click(https://click.palletsprojects.com/en/stable/)]** for CLI framework
* **[Peewee](https://docs.peewee-orm.com/en/latest/)** ORM
* **[just](https://github.com/casey/just)** as task launcher

## Installation

Create a Python virtual environment and install dependencies:

```bash
just virtualenv
source env/bin/activate
just run-taskmanager
```

## Development Workflow

The project includes several helpers in the `justfile` to streamline common development tasks (e.g., running the app, linting, testing).
