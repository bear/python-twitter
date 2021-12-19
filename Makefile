SUPPORTED_VERSIONS = 2.7.15 3.6.5 pypy-5.7.1 pypy3.5-6.0.0

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
	for version in $(SUPPORTED_VERSIONS) ; do \
		pyenv install -s $$version; \
	done
	pyenv local $(SUPPORTED_VERSIONS)

dev: pyenv env
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
	pytest -s
	#python setup.py test

tox: clean
	tox

coverage: clean
	coverage run --source=twitter setup.py test --addopts "--ignore=venv"
	coverage html
	coverage report

update-pyenv:
	cd /opt/circleci/.pyenv/plugins/python-build/../.. && git pull && cd -

ci: update-pyenv pyenv dev tox
	CODECOV_TOKEN=`cat .codecov-token` codecov

build: clean
	python setup.py check
	python setup.py sdist
	python setup.py bdist_wheel

upload: clean
	pyenv 2.7.15
	python setup.py sdist upload
	python setup.py bdist_wheel upload
	pyenv 3.6.5
	python setup.py bdist_wheel upload
	pyenv local $(SUPPORTED_VERSIONS)
