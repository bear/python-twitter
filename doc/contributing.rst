Contributing
------------

Getting the code
================

The code is hosted at `Github <https://github.com/bear/python-twitter>`_.

Check out the latest development version anonymously with::

    $ git clone git://github.com/bear/python-twitter.git
    $ cd python-twitter

Setting up a development environment can be handled automatically with ``make``
or via an existing virtual enviroment. To use ``make`` type the following
commands::

    $ make env-devel
    $ . env/bin/activate

The first command will create a virtual environment in the ``env/`` directory and install
the required dependencies for you. The second will activate the virtual
environment so that you can start working on the library.

If you would prefer to use an existing installation of virtualenvwrapper or
similar, you can install the required dependencies with::

    $ pip install requirements.devel.txt

or::

    $ make deps-devel

which will install the required dependencies for development of the library. 

Testing
=======

Once you have your development environment set up, you can run::

    $ make test

to ensure that all tests are currently passing before starting work. You can
also check test coverage by running::

    $ make coverage

Pull requests are welcome or, if you are having trouble, please open an issue on
GitHub.
