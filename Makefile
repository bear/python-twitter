DOCOPTIONS = html
DOCDIR = doc

help:
	@echo "  env-devel   create a development environment using virtualenv"
	@echo "  env-prod    create a production environment without development dependencies"
	@echo "  deps-devel  install dependencies for development and testing"
	@echo "  deps-prod   install only production dependencies"
	@echo "  docs        build documentation"
	@echo "  clean       remove unwanted stuff"
	@echo "  lint        check style with flake8"
	@echo "  test        run tests"
	@echo "  coverage    run tests with code coverage"

env-devel:
	sudo easy_install pip && \
	sudo pip install --upgrade pip && \
	sudo pip install virtualenv && \
	virtualenv env && \
	. env/bin/activate && \
	make deps-devel

env-prod:
	sudo easy_install pip && \
	pip install virtualenv && \
	virtualenv env && \
	. env/bin/activate && \
	make deps-prod

deps-devel:
	pip install -r requirements.devel.txt

deps-prod:
	pip install -r requirements.txt

clean:
	rm -fr build
	rm -fr dist
	rm -fr env
	rm -fr doc/_build/*
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;

lint:
	flake8 twitter > violations.flake8.txt

docs:
	$(MAKE) -C $(DOCDIR) html

coverage:
	py.test --cov=twitter

test:
	py.test	

build: clean
	python setup.py sdist
	python setup.py bdist_wheel

upload: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload
