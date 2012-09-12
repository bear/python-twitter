=Python Twitter=

_A Python wrapper around the Twitter API_

Author: `The Python-Twitter Developers <python-twitter@googlegroups.com>`

==Introduction==

This library provides a pure Python interface for the Twitter API.

Twitter (http://twitter.com) provides a service that allows people to
connect via the web, IM, and SMS.  Twitter exposes a web services API
(http://dev.twitter.com/doc) and this library is intended to make
it even easier for Python programmers to use.

==Building==

*From source:*

Install the dependencies:

  SimpleJson
    http://cheeseshop.python.org/pypi/simplejson

  SimpleGeo's OAuth2
    http://github.com/simplegeo/python-oauth2 or
    http://pypi.python.org/pypi/oauth2

  HTTPLib2 (installed along with oauth2 if you use setuptools)
    http://code.google.com/p/httplib2/

Download the latest python-twitter library from:

  http://code.google.com/p/python-twitter/

Extract the source distribution and run:

{{{
  $ python setup.py build
  $ python setup.py install
}}}

*Testing*

With setuptools installed:

{{{
  $ python setup.py test
}}}

Without setuptools installed:

{{{
  $ python twitter_test.py
}}}

==Getting the code==

View the trunk at:

  http://code.google.com/p/python-twitter/source/

Check out the latest development version anonymously with:

{{{
   $ hg clone http://python-twitter.googlecode.com/hg/ python-twitter
   $ cd python-twitter
   $ hg update dev
}}}

==Documentation==

View the last release API documentation at:

  http://dev.twitter.com/doc

==Using==

The library provides a Python wrapper around the Twitter API and
the Twitter data model.

*Model:*

The three model classes are twitter.Status, twitter.User, and
twitter.DirectMessage.  The API methods return instances of these
classes.

To read the full API for twitter.Status, twitter.User, or
twitter.DirectMessage, run:

{{{
  $ pydoc twitter.Status
  $ pydoc twitter.User
  $ pydoc twitter.DirectMessage
}}}

*API:*

The API is exposed via the twitter.Api class.

To create an instance of the twitter.Api class:

{{{
  >>> import twitter
  >>> api = twitter.Api()
}}}

To create an instance of the twitter.Api with login credentials (many API
calls required the client to be authenticated.)

The python-twitter library now only supports oAuth authentication as the
Twitter devs have indicated that oAuth is the only method that will be
supported moving forward.

  >>> api = twitter.Api(consumer_key='consumer_key',
                        consumer_secret='consumer_secret',
                        access_token_key='access_token',
                        access_token_secret='access_token_secret')

To see if your credentials are successful:
 NOTE - much more than the small sample given here will print

  >>> print api.VerifyCredentials()
  {"id": 16133, "location": "Philadelphia", "name": "bear"}

To fetch the most recently posted public Twitter status messages:

{{{
  >>> statuses = api.GetPublicTimeline()
  >>> print [s.user.name for s in statuses]
  [u'DeWitt', u'Kesuke Miyagi', u'ev', u'Buzz Andersen', u'Biz Stone'] 
}}}

To fetch a single user's public status messages, where "user" is either
a Twitter "short name" or their user id.

{{{
  >>> statuses = api.GetUserTimeline(user)
  >>> print [s.text for s in statuses]
}}}

To fetch a list a user's friends (requires authentication):

{{{
  >>> users = api.GetFriends()
  >>> print [u.name for u in users]
}}}

To post a Twitter status message (requires authentication):

{{{
  >>> status = api.PostUpdate('I love python-twitter!')
  >>> print status.text
  I love python-twitter!
}}}

There are many more API methods, to read the full API documentation:

{{{
  $ pydoc twitter.Api
}}}

==Todo==

Patches and bug reports are welcome, just please keep the style
consistent with the original source.

Add more example scripts.

The twitter.Status and twitter.User classes are going to be hard
to keep in sync with the API if the API changes.  More of the
code could probably be written with introspection.

Statement coverage of twitter_test is only about 80% of twitter.py.

The twitter.Status and twitter.User classes could perform more
validation on the property setters.

==More Information==

Please visit http://groups.google.com/group/python-twitter for more discussion.

==Contributors==

Additional thanks to Pierre-Jean Coudert, Omar Kilani, Jodok Batlogg,
edleaf, glen.tregoning, Brad Choate, Jim Cortez, Jason Lemoine, Thomas
Dyson, Robert Laquey, Hameedullah Khan, Mike Taylor, DeWitt Clinton, 
and the rest of the python-twitter mailing list.

==License==

{{{
  Copyright 2007 The Python-Twitter Developers
  
  Licensed under the Apache License, Version 2.0 (the 'License');
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  
      http://www.apache.org/licenses/LICENSE-2.0
  
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an 'AS IS' BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
}}}
