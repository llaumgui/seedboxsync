---
title: Development Backend
summary: Development guide for SeedboxSync
---

This section covers development for the **SeedboxSync backend**.

SeedboxSync is build with [Cement](https://builtoncement.com/) and [Peewee](http://docs.peewee-orm.com/en/latest/) from v3.

## Installation

Create a Python virtual environment and install dependencies:

```bash
make virtualenv
source env/bin/activate
```

## Development Workflow

The project includes several helpers in the `Makefile` to streamline common development tasks (e.g., running the app, linting, testing).
