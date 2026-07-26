---
title: Development
summary: Development guide for SeedboxSync
---

This section covers development for the **SeedboxSync backend**.

## Tech Stack

* **[just](https://github.com/casey/Just)** as task launcher
* **Python 3**:

    * **[uv](https://docs.astral.sh/uv/)** as Python package manager.
    * **[Click](https://click.palletsprojects.com/en/stable/)** for CLI framework
    * **[Flask](https://flask.palletsprojects.com/en/stable/)** / Flask-Caching / Flask-Babel / Flask-RESTX for webui
    * **[Peewee](https://docs.peewee-orm.com/en/latest/)** ORM

* **Node.js**:
    * **[pnpm](https://pnpm.io)** as Node.js package manager
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

### Install Node.js stack

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
just run-front
```

Run command line:

```bash
seedboxsync --help
```

### Run Node.js stack

Build on change:

```bash
pnpm dev
```

Simple build:

```bash
pnpm build
```

## Testing

```bash
just test
```

## Use Just

```bash
$ just
Available recipes:
    basedpyright    # Run static type checking on Python source code using basedpyright
    clean           # Remove Python bytecode files (*.pyc) and build artifacts
    comply          # Check Python code quality and style using Ruff
    default         # Display available recipes and their descriptions
    dist            # Build frontend assets and package the Python distribution via Flit
    doc-gh-deploy   # Deploy on GitHub the static documentation site using ProperDocs
    docker-build    # Build the Docker container image
    docs            # Build static documentation site using ProperDocs
    docs-serve      # Serve live documentation preview with auto-reloading using ProperDocs
    format *args    # Format Python code and automatically fix safe issues using Ruff
    hadolint        # Lint the Dockerfile for best practices and security issues (need hadolint)
    i18n-compile    # Compile translation catalog files (.po to .mo)
    i18n-extract    # Extract translatable strings to .pot, update .po catalog files, and compile .mo binaries
    i18n-update     # Update existing translation files (.po) against the template (.pot)
    markdownlint    # Lint Markdown files for syntax and formatting rules (need markdownlint)
    mypy            # Run static type checking on Python source code using Mypy
    nodejs-build    # Build and bundle frontend assets for production
    nodejs-dev      # Start Node.js frontend development server
    nodejs-lint     # Run linter for Node.js frontend code/assets
    publish         # Build distribution packages and publish to PyPI using Flit
    pytest          # Run Pytest suite with terminal output and HTML coverage report
    pytest-ci       # Run Pytest suite for CI with XML coverage output
    run-front       # Run the Flask development server with hot-reloading enabled
    run-taskmanager # Run the Huey background task worker with 2 threads
    test            # Run all local linters followed by the full test suite
    test-ci         # Run the full validation and testing pipeline for CI
    type-checking   # Run static type checking on Python source code
    virtualenv      # Recreate the Python virtual environment (.venv) using uv and install dependencies in editable mode
```
