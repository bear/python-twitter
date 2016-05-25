Changelog
---------

Version 3.1
==========

What's New
____________

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
______________

* :py:func:`twitter.api.Api.GetStatus()` Now accepts the keyword argument ``include_ext_alt_text`` which will request alt text to be included with the Status object being returned (if available). Defaults to ``True``.

* ``[model].__repr__()`` functions have been revised for better Unicode compatibility. If you notice any weirdness, please let us know.

* :py:func:`twitter.api.Api()` no longer accepts the ``shortner`` parameter; however, see ``examples/shorten_url.py`` for an example of how to use a URL shortener with the API.

* :py:func:`twitter.api.Api._Encode()` and :py:func:`twitter.api.Api._EncodePostData()` have both been refactored out of the API.

* :py:class:`twitter.models.Media` now has an attribute ``ext_alt_text`` for alt (hover) text for images posted to Twitter.

* :py:class:`twitter.models.Status` no longer has the properties ``relative_created_at``, ``now``, or ``Now``. If you require a relative time, we suggest using a third-party library.

* Updated examples, specifically ``examples/twitter-to-xhtml.py``, ``examples/view_friends.py``, ``examples/shorten_url.py``

* Updated ``get_access_token.py`` script to be python3 compatible.
