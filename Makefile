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

env:
	@pyenv install -s 3.5.1
	-@pyenv uninstall pythontwitter
	@pyenv virtualenv 3.5.1 pythontwitter
	@echo 'pythontwitter' >> .python-version
	@pip install pip --upgrade

production:
	@pip install -r requirements.txt

development:
	@pip install -r requirements.devel.txt

clean:
	pyenv uninstall pythontwitter
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
