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

Run::

    $ python test.py

If you would like to see coverage information and have `Nose <https://nose.readthedocs.org>`_ installed::

    $ nosetests --with-coverage


Getting the code
================

The code is hosted at `Github <https://github.com/bear/python-twitter>`_.

Check out the latest development version anonymously with::

$ git clone git://github.com/bear/python-twitter.git
$ cd python-twitter