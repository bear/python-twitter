Installation & Testing
------------

Installation
============

**From PyPI** ::

    $ pip install python-twitter


**From source**

Install the dependencies:

- `Requests <http://docs.python-requests.org/en/latest/>`_
- `Requests OAuthlib <https://requests-oauthlib.readthedocs.io/en/latest/>`_

Alternatively use `pip`::

    $ pip install -r requirements.txt

Download the latest `python-twitter` library from: https://github.com/bear/python-twitter/

Extract the source distribution and run::

    $ python setup.py build
    $ python setup.py install


Testing
=======

The following requires ``pip install pytest`` and ``pip install pytest-cov``. Run::

    $ make test

If you would like to see coverage information:: 

    $ make coverage


Getting the code
================

The code is hosted at `Github <https://github.com/bear/python-twitter>`_.

Check out the latest development version anonymously with::

$ git clone git://github.com/bear/python-twitter.git
$ cd python-twitter
