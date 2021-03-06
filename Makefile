.PHONY: clean virtualenv test docker dist dist-upload

clean:
	find . -name '*.py[co]' -delete

virtualenv:
	virtualenv --prompt '|> seedboxsync <| ' env
	env/bin/pip install -r requirements-dev.txt
	env/bin/python setup.py develop
	@echo
	@echo "VirtualENV Setup Complete. Now run: source env/bin/activate"
	@echo

test:
	flake8 seedboxsync --count --show-source --statistics
	coverage erase
	coverage run --source=seedboxsync -m pytest \
		-v \
		--cov-report=term \
		--cov-report=html:coverage-report \
		--junitxml=coverage-report/pytest-report.xml \
		tests/
	coverage xml -i

docker: clean
	docker build -t seedboxsync:latest .

dist: clean
	rm -rf build/* dist/*
	python setup.py sdist
	python setup.py bdist_wheel

dist-upload:
	twine upload dist/*