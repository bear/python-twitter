Contributing
------------

Getting the code
================

The code is hosted at `Github <https://github.com/bear/python-twitter>`_.

Check out the latest development version anonymously with::

    $ git clone git://github.com/bear/python-twitter.git
    $ cd python-twitter


.. _dev_envs:

Development Environments
========================

Recommended (pyenv + pyenv-virtualenv)
+++++++++++++++++++

The best way to get set up for working on the library is to have an
installation of `pyenv <https://github.com/yyuu/pyenv>`_ available and
configured for your preferred version of python. Please see the installation
instructions for pyenv for more information on getting the code.

It is also recommended that you install the `virtual environment plugin
<https://github.com/yyuu/pyenv-virtualenv>`_ for pyenv in order to install the
library's dependencies. The rest of this guide will be based on this setup.

Automated Setup
_______________

If you'd like to have the set up an environment completely automated, then the
following is for you. This will create a virtual environment called
``pythontwitter`` and install Python 3.5.1 and all the dependencies::

    $ make env production

for a production environment, or::

    $ make env development

for a development enviroment. To delete the virtualenviroment, run::

    $ make clean

If you'd rather go through the steps manually, they are reproduced below.

Manual Setup
____________
To get running, first install the version of python you want to use with
pyenv::

    $ pyenv install 3.5.1

Next we'll create a virtual environment to install the project's dependencies without cluttering up the
system version of python::

    $ pyenv virtualenv 3.5.1 pythontwitter
    $ pyenv local pythontwitter

At this point, your virtual environment will be installed and activated. Next,
we'll install the project's dependencies. If you're working in a production
environment where you will not be working on the library itself, running::

    $ pip install -r requirements.txt

will take care of the dependencies for using the library, but exclude things like testing and building documentation.

If you are planning on working on the library and want the ability to run tests
or build documentation locally, then run::

    $ pip install -r requirements.devel.txt

while your virtual environment is active and you should be ready to go.


Alternative
+++++++++++

If you would prefer to use an existing python installation or virtualenvwrapper or
similar, you install the production dependencies with::

    $ pip install -r requirements.txt


or the development dependencies with::

    $ pip install -r requirements.devel.txt


which will install the required dependencies for development of the library.

Testing
=======

Once you have your development environment set up and the development
dependencies installed, you can run::

    $ make test

to ensure that all tests are currently passing before starting work. You can
also check test coverage by running::

    $ make coverage

Pull requests are welcome or, if you are having trouble, please open an issue on
GitHub. If at all possible, please include tests for any changes.
