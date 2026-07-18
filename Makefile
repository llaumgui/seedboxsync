.PHONY: virtualenv run i18n-extract i18n-update i18n-compile test test-ci pytest pytest-xml test-core  comply markdownlint hadolint mypy npm-lint docs docs-serve clean dist publish

virtualenv:
	virtualenv --prompt '|> seedboxsync <| ' env
	env/bin/pip install -e ".[dev]"
	@echo
	@echo "VirtualENV Setup Complete. Now run: source env/bin/activate"
	@echo

run:
	export FLASK_SECRET_KEY=dev ; \
	export FLASK_CACHE_TYPE=NullCache ; \
	flask --app seedboxsync.app:app run --debug

run-taskmanager:
	export FLASK_SECRET_KEY=dev ; \
	export FLASK_CACHE_TYPE=NullCache ; \
	huey_consumer seedboxsync.taskmanager.huey -w 2 -k thread

run-gunicorn:
	export FLASK_SECRET_KEY=gunicorn ; \
	gunicorn -w 1 -b 0.0.0.0:5000 seedboxsync.app:app

i18n-extract:
	pybabel extract -F babel.cfg -o seedboxsync/front/messages.pot .

i18n-update:
	pybabel update -i seedboxsync/front/messages.pot -d seedboxsync/front/translations

i18n-compile:
	pybabel compile -d seedboxsync/front/translations

test: comply mypy pytest markdownlint hadolint npm-lint

test-ci: comply mypy i18n-compile pytest-xml

pytest:
	python -m pytest -v --cov=seedboxsync --cov-report=term --cov-report=html:coverage-report --capture=sys tests/

pytest-xml:
	python -m pytest -v --cov=seedboxsync --cov-report=term --cov-report=xml --capture=sys tests/

comply:
	flake8 seedboxsync/ tests/

markdownlint:
	markdownlint -c .markdownlint.yaml *.md docs/

hadolint:
	hadolint Dockerfile

mypy:
	mypy

black:
	black tests seedboxsync

npm-lint:
	npm run test:lint

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

publish:
	flit publish