
help:
	@echo "  env         install all production dependencies"
	@echo "  dev         install all dev and production dependencies (virtualenv is assumed)"
	@echo "  docs        build documentation"
	@echo "  clean       remove unwanted stuff"
	@echo "  lint        check style with flake8"
	@echo "  test        run tests"
	@echo "  coverage    run tests with code coverage"

env:
	pip install -Ur requirements.txt

pyenv:
	pyenv install -s 2.7.11
	pyenv install -s 3.6.1
	pyenv install -s pypy-5.3.1
	# pyenv install -s pypy3-2.4.0
	pyenv local 2.7.11 3.6.1 pypy-5.3.1 # pypy3-2.4.0

dev: env pyenv
	pip install -Ur requirements.testing.txt

info:
	@python --version
	@pyenv --version
	@pip --version

clean:
	rm -fr build
	rm -fr dist
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' ! -name '*.un~' -exec rm -f {} \;

docs:
	$(MAKE) -C doc html

lint:
	pycodestyle --config={toxinidir}/setup.cfg twitter tests

test: lint
	python setup.py test

tox: clean
	tox

coverage: clean
	coverage run --source=twitter setup.py test --addopts "--ignore=venv"
	coverage html
	coverage report

ci: pyenv
	tox
	CODECOV_TOKEN=`cat .codecov-token` codecov

build: clean
	python setup.py check
	python setup.py sdist
	python setup.py bdist_wheel

upload: clean
	pyenv 2.7.11
	python setup.py sdist upload
	python setup.py bdist_wheel upload
	pyenv 3.6.1
	python setup.py bdist_wheel upload
	pyenv local 2.7.11 3.6.1 pypy-5.3.1
