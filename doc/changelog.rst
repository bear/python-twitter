Changelog
---------

Version 3.1
==========

What's New
____________

* :py:func:`twitter.api.Api.PostMediaMetadata()` Method allows the posting of alt text (hover text) to a photo on Twitter. Note that it appears that you have to call this method prior to attaching the photo to a status.

* Updated examples, specifically ``examples/twitter-to-xhtml.py``, ``examples/view_friends.py``, ``examples/shorten_url.py``

* Updated ``get_access_token.py`` script to be python3 compatible.

* A couple new methods have been added related to showing the connections between two users:

  * :py:func:`twitter.api.Api.ShowFriendship()` shows the connection between two users (i.e., are they following each other?)
  * :py:func:`twitter.api.Api.IncomingFriendship()` shows all of the authenticated user's pending follower requests (if the user has set their account to private).
  * :py:func:`twitter.api.Api.OutgoingFriendship()` shows the authenticated user's request to follow other users (i.e. the user has attempted to follow a private account).


What's Changed
______________

* :py:func:`twitter.api.Api.GetStatus()` Now accepts the keyword argument ``include_ext_alt_text`` which will request alt text to be included with the Status object being returned (if available). Defaults to ``True``.

* ``[model].__repr__()`` functions have been revised for better Unicode compatibility. If you notice any weirdness, please let us know.

* :py:func:`twitter.api.Api()` no longer accepts the ``shortner`` parameter; however, see ``examples/shorten_url.py`` for an example of how to use a URL shortener with the API.

* :py:func:`twitter.api.Api._Encode()` and :py:func:`twitter.api.Api._EncodePostData()` have both been refactored out of the API.

* :py:class:`twitter.models.Media` now has an attribute ``ext_alt_text`` for alt (hover) text for images posted to Twitter.

* :py:class:`twitter.models.Status` no longer has the properties ``relative_created_at``, ``now``, or ``Now``.
