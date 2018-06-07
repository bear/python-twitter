Changelog
---------

Version 3.4.2
=============

Bugfixes:

* Allow upload of GIFs with size up to 15mb. See `#538 <https://github.com/bear/python-twitter/pull/538>`_

Version 3.4.1
=============

Bugfixes:

* Fix an issue where :py:func:`twitter.twitter_utils.calc_expected_status_length` was failing for python 2 due to a failure to convert a bytes string to unicode. `Github issue #546 <https://github.com/bear/python-twitter/issues/546>`_.

* Documentation fix for :py:func:`twitter.api.Api.UsersLookup`. UsersLookup can take a string or a list and properly parses both of them now. Github issues `#535 <https://github.com/bear/python-twitter/issues/535>`_ and `#549 <https://github.com/bear/python-twitter/issues/549>`_.

* Properly decode response content for :py:func:`twitter.twitter_utils.http_to_file`. `Github issue #521 <https://github.com/bear/python-twitter/issues/521>`_.

* Fix an issue with loading extended_tweet entities from Streaming API where tweets would be truncated when converting to a :py:class:`twitter.models.Status`. Github issues `#491 <https://github.com/bear/python-twitter/issues/491>`_ and `#506 <https://github.com/bear/python-twitter/issues/506>`_.

Version 3.4
===========

Deprecations
++++++++++++

* :py:func:`twitter.api.Api.UpdateBackgroundImage`. Please make sure that your code does not call this function as it will now return a hard error. There is no replacement function. This was deprecated by Twitter around July 2015.

* :py:func:`twitter.api.Api.PostMedia` has been removed. Please use :py:func:`twitter.api.Api.PostUpdate` instead.

* :py:func:`twitter.api.Api.PostMultipleMedia`. Please use :py:func:`twitter.api.Api.PostUpdate` instead.


Version 3.3.1
=============

* Adds support for 280 character limit.


Version 3.3
=============

* Adds application only authentication. See `Twitter's documentation for details <https://dev.twitter.com/oauth/application-only>`_. To use application only authentication, pass `application_only_auth` when creating the Api; the bearer token will be automatically retrieved.

* Adds function :py:func:`twitter.api.GetAppOnlyAuthToken`

* Adds `filter_level` keyword argument for :py:func:`twitter.api.GetStreamFilter`, :py:func:`twitter.api.GetUserStream`

* Adds `proxies` keyword argument for creating an Api instance. Pass a dictionary of proxies for the request to pass through, if not specified allows requests lib to use environmental variables for proxy if any.

* Adds support for `quoted_status` to the :py:class:`twitter.models.Status` model.


Version 3.2.1
=============

* :py:func:`twitter.twitter_utils.calc_expected_status_length` should now function properly. Previously, URLs would be counted incorrectly. See `PR #416 <https://github.com/bear/python-twitter/pull/416>`_

* :py:func:`twitter.api.Api.PostUpdates` now passes any keyword arguments on the edge case that only one tweet was actually being posted.


Version 3.2
===========

Deprecations
++++++++++++

Nothing is being deprecationed this version, however here's what's being deprecated as of v. 3.3.0:

* :py:func:`twitter.api.Api.UpdateBackgroundImage`. Please make sure that your code does not call this function as it will be returning a hard error. There is no replace function. This was deprecated by Twitter around July 2015.

* :py:func:`twitter.api.Api.PostMedia` will be removed. Please use :py:func:`twitter.api.Api.PostUpdate` instead.

* :py:func:`twitter.api.Api.PostMultipleMedia`. Please use :py:func:`twitter.api.Api.PostUpdate` instead.

* :py:func:`twitter.api.GetFriends` will no longer accept a `cursor` or `count` parameter. Please use :py:func:`twitter.api.GetFriendsPaged` instead.

* :py:func:`twitter.api.GetFollowers` will no longer accept a `cursor` or `count` parameter. Please use :py:func:`twitter.api.GetFollowersPaged` instead.


What's New
++++++++++

* We've added new deprecation warnings, so it's easier to track when things go away. All of python-twitter's deprecation warnings will be a subclass of :py:class:`twitter.error.PythonTwitterDeprecationWarning` and will have a version number associated with them such as :py:class:`twitter.error.PythonTwitterDeprecationWarning330`.


* :py:class:`twitter.models.User` now contains a ``following`` attribute, which describes whether the authenticated user is following the User. `PR #351 <https://github.com/bear/python-twitter/pull/351>`_

* :py:class:`twitter.models.DirectMessage` contains a full :py:class:`twitter.models.User` object for both the ``DirectMessage.sender`` and ``DirectMessage.recipient`` properties. `PR #384 <https://github.com/bear/python-twitter/pull/384>`_.

* You can now upload Quicktime movies (``*.mov``). `PR #372 <https://github.com/bear/python-twitter/pull/372>`_.

* If you have a whitelisted app, you can now get the authenticated user's email address through a call to :py:func:`twitter.api.Api.VerifyCredentials()`. If your app isn't whitelisted, no error is returned. `PR #376 <https://github.com/bear/python-twitter/pull/376>`_.

* Google App Engine support has been reintegrated into the library. Check out `PR #383 <https://github.com/bear/python-twitter/pull/383>`_.

* `video_info` is now available on a `twitter.models.Media` object, which allows access to video urls/bitrates/etc. in the `extended_entities` node of a tweet.

What's Changed
++++++++++++++

* :py:class:`twitter.models.Trend`'s `volume` attribute has been renamed `tweet_volume` in line with Twitter's naming convention. This change should allow users to access the number of tweets being tweeted for a given Trend. `PR #375 <https://github.com/bear/python-twitter/pull/375>`_

* :py:class:`twitter.ratelimit.RateLimit` should behave better now and adds a 1-second padding to requests after sleeping.

* :py:class:`twitter.ratelimit.RateLimit` now keeps track of your rate limit status even if you don't have ``sleep_on_rate_limit`` set to ``True`` when instatiating the API. If you want to add different behavior on hitting a rate limit, you should be able to now by querying the rate limit object. See `PR #370 <https://github.com/bear/python-twitter/pull/370>`_ for the technical details of the change. There should be no difference in behavior for the defaults, but let us know.


Bugfixes
++++++++

* :py:class:`twitter.models.Media` again contains a ``sizes`` attribute, which was missed back in the Version 3.0 release. `PR #360 <https://github.com/bear/python-twitter/pull/360>`_

* The previously bloated :py:func:`twitter.api.Api.UploadMediaChunked()` function has been broken out into three related functions and fixes two an incompatibility with python 2.7. Behavior remains the same, but this should simplify matters. `PR #347 <https://github.com/bear/python-twitter/pull/347>`_

* Fix for :py:func:`twitter.api.Api.PostUpdate()` where a passing an integer to the ``media`` parameter would cause an iteration error to occur. `PR #347 <https://github.com/bear/python-twitter/pull/347>`_

* Fix for 401 errors that were occuring in the Streaming Endpoints. `PR #364 <https://github.com/bear/python-twitter/pull/364>`_



Version 3.1
==========

What's New
++++++++++

* :py:func:`twitter.api.Api.PostMediaMetadata()` Method allows the posting of alt text (hover text) to a photo on Twitter. Note that it appears that you have to call this method prior to attaching the photo to a status.

* A couple new methods have been added related to showing the connections between two users:

  * :py:func:`twitter.api.Api.ShowFriendship()` shows the connection between two users (i.e., are they following each other?)
  * :py:func:`twitter.api.Api.IncomingFriendship()` shows all of the authenticated user's pending follower requests (if the user has set their account to private).
  * :py:func:`twitter.api.Api.OutgoingFriendship()` shows the authenticated user's request to follow other users (i.e. the user has attempted to follow a private account).

* Several methods were added related to muting users:

  * :py:func:`twitter.api.Api.GetMutes()` returns **all** users the currently authenticated user is muting (as ``twitter.models.User`` objects).
  * :py:func:`twitter.api.Api.GetMutesPaged()` returns a page of ``twitter.models.User`` objects.
  * :py:func:`twitter.api.Api.GetMutesIDs()` returns **all** of the users the currently authenticated user is muting as integers.
  * :py:func:`twitter.api.Api.GetMutesIDsPaged()` returns a single page of the users the currently authenticated user is muting as integers.


What's Changed
++++++++++++++

* :py:func:`twitter.api.Api.GetStatus()` Now accepts the keyword argument ``include_ext_alt_text`` which will request alt text to be included with the Status object being returned (if available). Defaults to ``True``.

* ``[model].__repr__()`` functions have been revised for better Unicode compatibility. If you notice any weirdness, please let us know.

* :py:func:`twitter.api.Api()` no longer accepts the ``shortner`` parameter; however, see ``examples/shorten_url.py`` for an example of how to use a URL shortener with the API.

* :py:func:`twitter.api.Api._Encode()` and :py:func:`twitter.api.Api._EncodePostData()` have both been refactored out of the API.

* :py:class:`twitter.models.Media` now has an attribute ``ext_alt_text`` for alt (hover) text for images posted to Twitter.

* :py:class:`twitter.models.Status` no longer has the properties ``relative_created_at``, ``now``, or ``Now``. If you require a relative time, we suggest using a third-party library.

* Updated examples, specifically ``examples/twitter-to-xhtml.py``, ``examples/view_friends.py``, ``examples/shorten_url.py``

* Updated ``get_access_token.py`` script to be python3 compatible.

* :py:func:`twitter.api.Api.GetStreamFilter()` now accepts an optional languages parameter as a list.
