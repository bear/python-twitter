Python Twitter

A Python wrapper around the Twitter API.

By the `Python-Twitter Developers <python-twitter@googlegroups.com>`_

.. image:: https://pypip.in/wheel/python-twitter/badge.png
    :target: https://pypi.python.org/pypi/python-twitter/
    :alt: Wheel Status

============
Introduction
============

This library provides a pure Python interface for the `Twitter API <https://dev.twitter.com/>`_. It works with Python versions from 2.6+. Python 3 support is under development.

`Twitter <http://twitter.com>`_ provides a service that allows people to connect via the web, IM, and SMS. Twitter exposes a `web services API <https://dev.twitter.com/overview/documentation>`_ and this library is intended to make it even easier for Python programmers to use.

==========
Installing
==========

You can install python-twitter using::

    $ pip install python-twitter

Testing::

    $ python test.py

================
Getting the code
================

The code is hosted at https://github.com/bear/python-twitter

Check out the latest development version anonymously with::

    $ git clone git://github.com/bear/python-twitter.git
    $ cd python-twitter

Setup a virtual environment and install dependencies:

	$ make env

Activate the virtual environment created:

	$ source env/bin/activate

Run tests:

	$ make test

To see other options available, run:

	$ make help


=============
Documentation
=============

View the last release API documentation at: https://dev.twitter.com/overview/documentation

=====
Using
=====

The library provides a Python wrapper around the Twitter API and the Twitter data model.

----
Using with Django
----

Additional template tags that expand tweet urls and urlize tweet text. See the django template tags available for use with python-twitter: https://github.com/radlws/python-twitter-django-tags

-----
Model
-----

The three model classes are ``twitter.Status``, ``twitter.User``, and ``twitter.DirectMessage``. The API methods return instances of these classes.

To read the full API for ``twitter.Status``, ``twitter.User``, or ``twitter.DirectMessage``, run::

    $ pydoc twitter.Status
    $ pydoc twitter.User
    $ pydoc twitter.DirectMessage

---
API
---

The API is exposed via the ``twitter.Api`` class.

The python-twitter library now only supports OAuth authentication as the Twitter devs have indicated that OAuth is the only method that will be supported moving forward.

To generate an Access Token you have to pick what type of access your application requires and then do one of the following:

- `Generate a token to access your own account <https://dev.twitter.com/oauth/overview/application-owner-access-tokens>`_
- `Generate a pin-based token <https://dev.twitter.com/oauth/pin-based>`_
- use the helper script `get_access_token.py <https://github.com/bear/python-twitter/blob/master/get_access_token.py>`_

For full details see the `Twitter OAuth Overview <https://dev.twitter.com/oauth/overview>`_

To create an instance of the ``twitter.Api`` with login credentials (Twitter now requires an OAuth Access Token for all API calls)::

    >>> import twitter
    >>> api = twitter.Api(consumer_key='consumer_key',
                          consumer_secret='consumer_secret',
                          access_token_key='access_token',
                          access_token_secret='access_token_secret')

To see if your credentials are successful::

    >>> print api.VerifyCredentials()
    {"id": 16133, "location": "Philadelphia", "name": "bear"}

**NOTE**: much more than the small sample given here will print

To fetch a single user's public status messages, where ``user`` is a Twitter *short name*::

    >>> statuses = api.GetUserTimeline(screen_name=user)
    >>> print [s.text for s in statuses]

To fetch a list a user's friends (requires authentication)::

    >>> users = api.GetFriends()
    >>> print [u.name for u in users]

To post a Twitter status message (requires authentication)::

    >>> status = api.PostUpdate('I love python-twitter!')
    >>> print status.text
    I love python-twitter!

There are many more API methods, to read the full API documentation::

    $ pydoc twitter.Api



----
Todo
----

Patches and bug reports are `welcome <https://github.com/bear/python-twitter/issues/new>`_, just please keep the style consistent with the original source.

Add more example scripts.

The twitter.Status and ``twitter.User`` classes are going to be hard to keep in sync with the API if the API changes. More of the code could probably be written with introspection.

Statement coverage of ``twitter_test`` is only about 80% of twitter.py.

The ``twitter.Status`` and ``twitter.User`` classes could perform more validation on the property setters.

----------------
More Information
----------------

Please visit `the google group <http://groups.google.com/group/python-twitter>`_ for more discussion.

------------
Contributors
------------

Originally two libraries by DeWitt Clinton and Mike Taylor which was then merged into python-twitter.

Now it's a full-on open source project with many contributors over time. See AUTHORS.rst for the complete list.

-------
License
-------

| Copyright 2007-2014 The Python-Twitter Developers
|
| Licensed under the Apache License, Version 2.0 (the 'License');
| you may not use this file except in compliance with the License.
| You may obtain a copy of the License at
|
|     http://www.apache.org/licenses/LICENSE-2.0
|
| Unless required by applicable law or agreed to in writing, software
| distributed under the License is distributed on an 'AS IS' BASIS,
| WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
| See the License for the specific language governing permissions and
| limitations under the License.
