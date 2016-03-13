Installation & Testing
------------

Installation
============

**From PyPI** ::

    $ pip install python-twitter


**From source**

Install the dependencies:

- `Requests <http://docs.python-requests.org/en/latest/>`_
- `Requests OAuthlib <https://requests-oauthlib.readthedocs.org/en/latest/>`_

Alternatively use `pip`::

    $ pip install -r requirements.txt

Download the latest `python-twitter` library from: https://github.com/bear/python-twitter/

Extract the source distribution and run::

    $ python setup.py build
    $ python setup.py install


Testing
=======

The above steps only install the dependencies for running the installed
python-twitter library; if you'd like to run the library's test suite, see
the :ref:`dev_envs` section for information on setting up a development
environment. Run::

    $ make test

If you would like to see coverage information::

    $ make coverage


Getting the code
================

The code is hosted at `Github <https://github.com/bear/python-twitter>`_.

Check out the latest development version anonymously with::

$ git clone git://github.com/bear/python-twitter.git
$ cd python-twitter

Please check out :ref:`dev_envs` for more information on setting up a development
environment and installing dependencies for working with the library.
