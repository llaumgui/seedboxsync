---
title: Development
summary: Development guide for SeedboxSync
---

This section covers development for the **SeedboxSync backend**.

## Tech Stack

* **[just](https://github.com/casey/just)** as task launcher
* **Python 3**:

    * **[uv](https://docs.astral.sh/uv/)** as Python package manager.
    * **[Click](https://click.palletsprojects.com/en/stable/)** for CLI framework
    * **[Flask](https://flask.palletsprojects.com/en/stable/)** / Flask-Caching / Flask-Babel / Flask-RESTX for webui
    * **[Peewee](https://docs.peewee-orm.com/en/latest/)** ORM

* **nodejs**:
    * **[pnpm](https://pnpm.io)** as nodejs package manager
    * **[Bulma](https://bulma.io/)** as CSS Framework
    * **[Alpine.js](https://alpinejs.dev/)** as JS framework
    * **[Vite](https://vite.dev)** as tooling

## Installation

### Install Python stack

Create a Python virtual environment and install dependencies:

```bash
just virtualenv
source env/bin/activate
```

### Install nodejs stack

```bash
pnpm i
```

## Run and launch

### Run Python stack

Run task-manager:

```bash
just run-taskmanager
```

Run Flask webui:

```bash
just run-web
```

Run command line:

```bash
seedboxsync --help
```

### Run nodejs stack

Build on change:

```bash
pnpm run dev
```

Simple build:

```bash
pnpm run build
```

## Testing

```bash
just test
```
