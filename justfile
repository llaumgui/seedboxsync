# Use .venv
export PATH := ".venv/bin:" + env_var('PATH')

set export
FLASK_SECRET_KEY := "dev"
FLASK_CACHE_TYPE := "NullCache"
HUEY_LOG_LEVEL := "DEBUG"

# Display available recipes and their descriptions
default:
    @just --list

# Recreate the Python virtual environment (.venv) using uv and install dependencies in editable mode
virtualenv:
    rm -rf .venv
    uv venv --prompt "|> seedboxsync <|" .venv
    uv pip install --python .venv/bin/python -e ".[dev]"
    @echo
    @echo "VirtualENV Setup Complete. Now run: source .venv/bin/activate"
    @echo

# Run the Flask development server with hot-reloading enabled
run-front:
    uv run flask --app seedboxsync.app:app run --debug

# Run the Huey background task worker with 2 threads
run-taskmanager:
    uv run huey_consumer seedboxsync.taskmanager.huey -w 2 -k thread

# Extract translatable strings to .pot, update .po catalog files, and compile .mo binaries
i18n-extract:
    uv run pybabel extract -F babel.cfg -o seedboxsync/front/messages.pot .
    @just i18n-update
    @just i18n-compile

# Update existing translation files (.po) against the template (.pot)
i18n-update:
    uv run pybabel update -i seedboxsync/front/messages.pot -d seedboxsync/front/translations

# Compile translation catalog files (.po to .mo)
i18n-compile:
    uv run pybabel compile -d seedboxsync/front/translations

# Check Python code quality and style using Ruff
comply:
    uv run ruff check

# Lint Markdown files for syntax and formatting rules (need markdownlint)
markdownlint:
    markdownlint -c .markdownlint.yaml *.md docs/

# Lint the Dockerfile for best practices and security issues (need hadolint)
hadolint:
    hadolint Dockerfile

# Run static type checking on Python source code using Mypy
mypy:
    uv run mypy

# Format Python code and automatically fix safe issues using Ruff
format *args:
    uv run ruff format
    uv run ruff check --fix {{args}}

# Run linter for Node.js frontend code/assets
nodejs-lint:
    pnpm test:lint

# Start Node.js frontend development server
nodejs-dev:
    pnpm dev

# Build and bundle frontend assets for production
nodejs-build:
    pnpm build

# Run Pytest suite with terminal output and HTML coverage report
pytest:
    uv run python -m pytest -v --cov=seedboxsync --cov-report=term --cov-report=html:coverage-report --capture=sys tests/

# Run Pytest suite for CI with XML coverage output
pytest-ci:
    uv run python -m pytest -v --cov=seedboxsync --cov-report=term --cov-report=xml --capture=sys tests/

# Run all local linters followed by the full test suite
test: comply mypy markdownlint hadolint nodejs-lint pytest

# Run the full validation and testing pipeline for CI
test-ci: comply mypy i18n-compile pytest-ci

# Build static documentation site using MkDocs
docs:
    mkdocs build

# Serve live documentation preview with auto-reloading
docs-serve:
    mkdocs serve

# Remove Python bytecode files (*.pyc) and build artifacts
clean:
    find . -name '*.py[co]' -delete

# Build the Docker container image
docker-build:
    podman build .

# Build frontend assets and package the Python distribution via Flit
dist: clean
    rm -rf dist/*
    pnpm build
    flit build

# Build distribution packages and publish to PyPI using Flit
publish: dist
    flit publish