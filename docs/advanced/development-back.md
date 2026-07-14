---
title: Development Backend
summary: Development guide for SeedboxSync
---

This section covers development for the **SeedboxSync backend**.

## Tech Stack

* **Python 3**
* **Click** for CLI framework
* **Peewee** ORM

## Installation

Create a Python virtual environment and install dependencies:

```bash
make virtualenv
source env/bin/activate
```

## Development Workflow

The project includes several helpers in the `Makefile` to streamline common development tasks (e.g., running the app, linting, testing).
