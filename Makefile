.PHONY: dev test test-ci test-pytest test-pytest-xml test-core virtualenv virtualenv-windows comply comply-fix comply-typing markdownlint docs docs-serve clean dist

dev:
	docker-compose up -d
	docker-compose exec seedboxsync pip install -r requirements-dev.txt
	docker-compose exec seedboxsync python setup.py develop
	docker-compose exec seedboxsync /bin/sh

test: comply markdownlint test-pytest

test-ci: comply test-pytest-xml

test-pytest:
	python -m pytest -v --cov=seedboxsync --cov-report=term --cov-report=html:coverage-report --capture=sys tests/

test-pytest-xml:
	python -m pytest -v --cov=seedboxsync --cov-report=term --cov-report=xml --capture=sys tests/

test-core: comply
	python -m pytest -v --cov=seedboxsync.core --cov-report=term --cov-report=html:coverage-report --capture=sys tests/core

virtualenv:
	virtualenv --prompt '|> seedboxsync <| ' env
	env/bin/pip install -e ".[dev]"
	@echo
	@echo "VirtualENV Setup Complete. Now run: source env/bin/activate"
	@echo

virtualenv-windows:
	virtualenv --prompt '|> seedboxsync <| ' env-windows
	env-windows\\Scripts\\pip.exe install -e ".[dev]"
	@echo
	@echo "VirtualENV Setup Complete. Now run: .\env-windows\Scripts\activate.ps1"
	@echo

comply:
	flake8 seedboxsync/ tests/

comply-fix:
	autopep8 -ri seedboxsync/ tests/

comply-typing:
	mypy ./seedboxsync

docs:
	mkdocs build

docs-serve:
	mkdocs serve

markdownlint:
	markdownlint -c .markdownlint.yaml *.md docs/

clean:
	find . -name '*.py[co]' -delete
	rm -rf doc/build

dist: clean
	rm -rf dist/*
	flit build
