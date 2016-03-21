Contributing
------------

Getting the code
================

The code is hosted at `Github <https://github.com/bear/python-twitter>`_.

Check out the latest development version anonymously with::

    $ git clone git://github.com/bear/python-twitter.git
    $ cd python-twitter

The following sections assuming that you have `pyenv
<https://github.com/yyuu/pyenv>`_ installed and working on your computer.

To install dependencies, run::

    $ make dev

This will install all of the required packages for the core library, testing,
and installation.

Testing
=======

Once you have your development environment set up, you can run::

    $ make test

to ensure that all tests are currently passing before starting work. You can
also check test coverage by running::

    $ make coverage

Pull requests are welcome or, if you are having trouble, please open an issue on
GitHub.
