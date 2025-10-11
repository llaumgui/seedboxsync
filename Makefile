.PHONY: virtualenv test test-ci pytest pytest-xml test-core  comply markdownlint hadolint mypy docs docs-serve clean dist

virtualenv:
	virtualenv --prompt '|> seedboxsync <| ' env
	env/bin/pip install -e ".[dev]"
	@echo
	@echo "VirtualENV Setup Complete. Now run: source env/bin/activate"
	@echo

test: comply mypy pytest markdownlint hadolint

test-ci: comply pytest-xml

pytest:
	python -m pytest -v --cov=seedboxsync --cov-report=term --cov-report=html:coverage-report --capture=sys tests/

pytest-xml:
	python -m pytest -v --cov=seedboxsync --cov-report=term --cov-report=xml --capture=sys tests/

test-core: comply
	python -m pytest -v --cov=seedboxsync.core --cov-report=term --cov-report=html:coverage-report --capture=sys tests/core

comply:
	flake8 seedboxsync/ tests/

markdownlint:
	markdownlint -c .markdownlint.yaml *.md docs/
hadolint:
	hadolint Dockerfile

mypy:
	mypy

docs:
	mkdocs build

docs-serve:
	mkdocs serve

clean:
	find . -name '*.py[co]' -delete
	rm -rf doc/build

dist: clean
	rm -rf dist/*
	flit build
