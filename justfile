set export
FLASK_SECRET_KEY := "dev"
FLASK_CACHE_TYPE := "NullCache"
HUEY_LOG_LEVEL := "DEBUG"

default:
    @just --list

virtualenv:
    virtualenv --prompt '|> seedboxsync <| ' env
    env/bin/pip install -e ".[dev]"
    @echo
    @echo "VirtualENV Setup Complete. Now run: source env/bin/activate"
    @echo

run-web:
    flask --app seedboxsync.app:app run --debug

run-taskmanager:
    huey_consumer seedboxsync.taskmanager.huey -w 2 -k thread

i18n-extract:
    pybabel extract -F babel.cfg -o seedboxsync/front/messages.pot .
    @just i18n-update

i18n-update:
    pybabel update -i seedboxsync/front/messages.pot -d seedboxsync/front/translations

i18n-compile:
    pybabel compile -d seedboxsync/front/translations

comply:
    ruff check

markdownlint:
    markdownlint -c .markdownlint.yaml *.md docs/

hadolint:
    hadolint Dockerfile

mypy:
    mypy

format *args:
    ruff format
    ruff check --fix {{args}}

npm-lint:
    npm run test:lint

npm-dev:
    npm run dev

npm-build:
    npm run build

lint: comply mypy markdownlint hadolint npm-lint

lint-ci: comply mypy

pytest:
    python -m pytest -v --cov=seedboxsync --cov-report=term --cov-report=html:coverage-report --capture=sys tests/

pytest-ci:
    python -m pytest -v --cov=seedboxsync --cov-report=term --cov-report=xml --capture=sys tests/

test: lint pytest

test-ci: lint-ci i18n-compile pytest-ci

docs:
    mkdocs build

docs-serve:
    mkdocs serve

clean:
    find . -name '*.py[co]' -delete
    rm -rf doc/build

dist: clean
    rm -rf dist/*
    npm run build
    flit build

publish: dist
    flit publish