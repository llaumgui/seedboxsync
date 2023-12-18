.PHONY: virtualenv test test-core comply comply-fix dist dist-upload

virtualenv:
	virtualenv --prompt '|> cement <| ' env
	env/bin/pip install -r requirements-dev.txt
	env/bin/python setup.py develop
	@echo
	@echo "VirtualENV Setup Complete. Now run: source env/bin/activate"
	@echo

test: comply
	python -m pytest -v --cov=seedboxsync --cov-report=term --cov-report=html:coverage-report tests/

test-core: comply
	python -m pytest -v --cov=seedboxsync.core --cov-report=term --cov-report=html:coverage-report tests/core

comply:
	flake8 seedboxsync/ tests/

comply-fix:
	autopep8 -ri cement/ tests/

clean:
	find . -name '*.py[co]' -delete
	rm -rf doc/build

dist: clean
	rm -rf dist/*
	python setup.py sdist
	python setup.py bdist_wheel

dist-upload:
	twine upload dist/*