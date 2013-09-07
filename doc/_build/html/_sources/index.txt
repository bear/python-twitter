.. python-twitter documentation master file, created by
   sphinx-quickstart on Fri Aug 30 14:37:05 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-twitter's documentation!
==========================================
**A Python wrapper around the Twitter API.**

Author: The Python-Twitter Developers <python-twitter@googlegroups.com>

Introduction
------------
This library provides a pure Python interface for the `Twitter API <https://dev.twitter.com/>`_. It works with Python versions from 2.5 to 2.7. Python 3 support is under development.

`Twitter <http://twitter.com>`_ provides a service that allows people to connect via the web, IM, and SMS. Twitter exposes a `web services API <http://dev.twitter.com/doc>`_ and this library is intended to make it even easier for Python programmers to use.


Building
--------
From source:

Install the dependencies:

- `SimpleJson <http://cheeseshop.python.org/pypi/simplejson>`_
- `Requests OAuthlib <https://requests-oauthlib.readthedocs.org/en/latest/>`_
- `HTTPLib2 <http://code.google.com/p/httplib2/>`_

This branch is currently in development to replace the OAuth and HTTPLib2 libarays with the following:

- `Requests <http://docs.python-requests.org/en/latest/>`_


Alternatively use `pip`::
 
    $ pip install -r requirements.txt

Download the latest `python-twitter` library from: http://code.google.com/p/python-twitter/

Extract the source distribution and run::

    $ python setup.py build
    $ python setup.py install


Testing
-------
With setuptools installed::

    $ python setup.py test


Without setuptools installed::

    $ python twitter_test.py


Getting the code
----------------
The code is hosted at `Github <https://github.com/bear/python-twitter>`_.

Check out the latest development version anonymously with::

$ git clone git://github.com/bear/python-twitter.git
$ cd python-twitter


.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

