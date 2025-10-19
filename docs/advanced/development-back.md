---
title: Development Backend
summary: Development guide for SeedboxSync
---

This section covers development for the **SeedboxSync backend**.

## Tech Stack

* **Python 3**
* **Cement** for CLI framework
* **Peewee** ORM

<p style="text-align:center;">
  <a href="https://www.python.org"><img alt="Python logo" src="../../images/python-powered-w-140x56.png" /></a> <a href="https://builtoncement.com"><img alt="SeedboxSync logo" src="../../images/logo-cement.png" /></a> <a href="https://docs.peewee-orm.com"><img alt="peewee logo" src="../../images/logo-peewee.png" /></a>
</p>

## Installation

Create a Python virtual environment and install dependencies:

```bash
make virtualenv
source env/bin/activate
```

## Development Workflow

The project includes several helpers in the `Makefile` to streamline common development tasks (e.g., running the app, linting, testing).
