# Use .venv
export PATH := ".venv/bin:" + env_var('PATH')

# Environment variables
set export
FLASK_SECRET_KEY := "dev"
FLASK_CACHE_TYPE := "NullCache"
HUEY_LOG_LEVEL := "DEBUG"

set default-list := true

# Alias
alias c := clean
alias build := dist
alias d := dist
alias docker := docker-build
alias front := run-front
alias task := run-taskmanager
alias update := dependencies-update
alias nodejs-update := nodejs-dependencies-update
alias python-update := python-dependencies-update


# ══════════════════════════════════════════════════════════════════════════════
# ⚙️  SYSTEM & ENVIRONMENT
# ══════════════════════════════════════════════════════════════════════════════

# Recreate the Python virtual environment (.venv) using uv and install dependencies in editable mode
virtualenv: clean
    rm -rf .venv
    uv venv --prompt "|> seedboxsync <|" .venv
    uv pip install --python .venv/bin/python -e ".[dev]"
    @echo
    @echo "VirtualENV Setup Complete. Now run: source .venv/bin/activate"
    @echo

# Update both Python and Node.js dependencies to their latest versions
dependencies-update: python-dependencies-update nodejs-dependencies-update


# ══════════════════════════════════════════════════════════════════════════════
# 🚀 LAUNCHER
# ══════════════════════════════════════════════════════════════════════════════

# Run the Flask development server with hot-reloading enabled
[group('🚀 Launcher')]
run-front: i18n-compile
    uv run flask --app seedboxsync.app:app run --debug

# Run the Huey background task worker with 2 threads
[group('🚀 Launcher')]
run-taskmanager:
    uv run huey_consumer seedboxsync.taskmanager.huey -w 2 -k thread


# ══════════════════════════════════════════════════════════════════════════════
# 🌐 INTERNATIONALIZATION (I18N)
# ══════════════════════════════════════════════════════════════════════════════

# Extract translatable strings to .pot, update .po catalog files, and compile .mo binaries
[group('🌐 Internationalization')]
i18n-extract:
    uv run pybabel extract -F babel.cfg -o seedboxsync/front/messages.pot .
    @just i18n-update
    @just i18n-compile

# Update existing translation files (.po) against the template (.pot)
[group('🌐 Internationalization')]
i18n-update:
    uv run pybabel update -i seedboxsync/front/messages.pot -d seedboxsync/front/translations

# Compile translation catalog files (.po to .mo)
[group('🌐 Internationalization')]
i18n-compile:
    uv run pybabel compile -d seedboxsync/front/translations


# ══════════════════════════════════════════════════════════════════════════════
# 🛠️ CODE QUALITY & LINTING
# ══════════════════════════════════════════════════════════════════════════════

# Check Python code quality and style using Ruff
[group('🛠️ Code quality & linting')]
[group('🐍 Python')]
comply:
    uv run ruff check

# Lint Markdown files for syntax and formatting rules (need markdownlint)
[group('🛠️ Code quality & linting')]
markdownlint:
    markdownlint -c .markdownlint.yaml *.md docs/

# Lint the Dockerfile for best practices and security issues (need hadolint)
[group('🛠️ Code quality & linting')]
hadolint:
    hadolint Dockerfile

# Run static type checking on Python source code using Mypy
[group('🛠️ Code quality & linting')]
[group('🐍 Python')]
mypy:
    uv run mypy

# Run static type checking on Python source code using basedpyright
[group('🛠️ Code quality & linting')]
[group('🐍 Python')]
basedpyright:
    uv run basedpyright

# Run static type checking on Python source code
[group('🛠️ Code quality & linting')]
[group('🐍 Python')]
type-checking: mypy basedpyright

# Format Python code and automatically fix safe issues using Ruff
[group('🛠️ Code quality & linting')]
[group('🐍 Python')]
format *args:
    uv run ruff format
    uv run ruff check --fix {{args}}

# Run linter for Node.js frontend code/assets
[group('🛠️ Code quality & linting')]
[group('🎨 Node.js')]
nodejs-lint:
    pnpm lint


# ══════════════════════════════════════════════════════════════════════════════
# 🧪 TESTING & CI
# ══════════════════════════════════════════════════════════════════════════════

# Run Pytest suite with terminal output and HTML coverage report
[group('🧪 Testing & CI')]
[group('🐍 Python')]
pytest:
    uv run python -m pytest -v --cov=seedboxsync --cov-report=term --cov-report=html:coverage-report --capture=sys tests/

# Run Pytest suite for CI with XML coverage output
[group('🧪 Testing & CI')]
[group('🐍 Python')]
pytest-ci:
    uv run python -m pytest -v --cov=seedboxsync --cov-report=term --cov-report=xml --capture=sys tests/

# Run all local linters followed by the full test suite
[group('🧪 Testing & CI')]
[group('🐍 Python')]
test: comply type-checking markdownlint hadolint nodejs-lint pytest

# Run the full validation and testing pipeline for CI
[group('🧪 Testing & CI')]
[group('🐍 Python')]
test-ci: comply type-checking i18n-compile pytest-ci

# Run Node.js frontend tests using Vitest
[group('🧪 Testing & CI')]
[group('🎨 Node.js')]
nodejs-test:
    pnpm test

# Run Node.js frontend tests using Vitest for CI with coverage report
[group('🧪 Testing & CI')]
[group('🎨 Node.js')]
nodejs-test-ci:
    pnpm test:ci


# ══════════════════════════════════════════════════════════════════════════════
# 🐍 PYTHON
# ══════════════════════════════════════════════════════════════════════════════

# Update Python dependencies to their latest versions
[group('🐍 Python')]
python-dependencies-update:
    uv lock --upgrade
    @just python-install

# Install Python dependencies in the virtual environment using uv
[group('🐍 Python')]
python-install *args:
    uv sync --locked {{args}}

# Install Python dependencies in the virtual environment using uv with extra dev dependencies
[group('🐍 Python')]
python-install-dev:
    @just python-install --extra dev


# ══════════════════════════════════════════════════════════════════════════════
# 🎨 NODE.JS / PNPM (Frontend)
# ══════════════════════════════════════════════════════════════════════════════

# Start Node.js frontend development server
[group('🎨 Node.js')]
nodejs-dev:
    pnpm dev

# Install Node.js dependencies using pnpm
[group('🎨 Node.js')]
nodejs-install:
    pnpm install --frozen-lockfile

# Build and bundle frontend assets for production
[group('🎨 Node.js')]
nodejs-build:
    pnpm build

# Update Node.js dependencies to their latest versions
[group('🎨 Node.js')]
nodejs-dependencies-update:
    pnpm update --latest

# ══════════════════════════════════════════════════════════════════════════════
# 📚 DOCUMENTATION
# ══════════════════════════════════════════════════════════════════════════════

# Build static documentation site using ProperDocs
[group('📚 Documentation')]
doc: pytest
    properdocs build

# Serve live documentation preview with auto-reloading using ProperDocs
[group('📚 Documentation')]
doc-serve:
    properdocs serve

# Prepare coverage and deploy on GitHub the static documentation site using ProperDocs
[group('📚 Documentation')]
doc-gh-deploy: i18n-compile pytest
    properdocs gh-deploy --force


# ══════════════════════════════════════════════════════════════════════════════
# 📦 BUILD, PACKAGING & CLEANUP
# ══════════════════════════════════════════════════════════════════════════════

# Remove Python bytecode files (*.pyc) and build artifacts
clean:
    rm -rf build/ dist/ seedboxsync/front/static/dist/ *.egg-info .eggs/
    rm -rf .pytest_cache .ruff_cache .mypy_cache coverage-report site/
    find ./seedboxsync -type d -name '__pycache__' -exec rm -rf {} +
    find ./seedboxsync -name '*.py[co]' -delete
    find ./seedboxsync -name '*.pot' -delete
    find ./seedboxsync -name '*.mo' -delete

# Build the Docker container image
docker-build:
    docker build .

# Build frontend assets and package the Python distribution via uv
dist: clean i18n-compile
    @just nodejs-build
    @SOURCE_DATE_EPOCH=$(git log -1 --format=%ct) uv build
    @just _dist-check

# Check the built distribution packages by running tests against them
_dist-check:
    uv run --isolated --no-project --with dist/*.whl pytest -v tests/
    uv run --isolated --no-project --with dist/*.tar.gz pytest -v tests/

# Build distribution packages and publish to PyPI using uv
publish: dist
    uv publish