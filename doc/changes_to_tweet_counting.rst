REST API Changes
=================

Information compiled on Sept 14, 2016.

``statuses/update`` Endpoint
----------------------------

``auto_populate_reply_metadata``
+++++++++++++++++++++++++++++++

* Default is ``false``

* Must have ``in_reply_to_status_id`` set.

* Unknown what happens if not set. Probably error (does it get posted?)

* If the status to which you're replying is deleted, tweet will fail to post.

``exclude_reply_user_ids``
++++++++++++++++++++++++++

* List of ``user_ids`` to remove from result of ``auto_populate_reply_metadata``.

* Doesn't apply to the first ``user_id``.

* If you try to remove it, this will be silently ignored by Twitter.

``attachment_url``
++++++++++++++++++

* Must be a status permalnk or a DM deep link.

* If it's anything else and included in this parameter, Twitter will return an error.


Most Other Endpoints
--------------------

``tweet_mode``
++++++++++++++

* Any endpoint that returns a tweet will accept this param.

* Must be in ``['compat', 'extended']``

* If ``tweet_mode == 'compat'``, then no ``extended_tweet`` node in the json returned.

* If ``tweet_mode == 'extended'``, then you'll get the ``extended_tweet`` node.


Errors
------
* 44 -> URL passed to attachment_url is invalid

* 385 -> Replied to deleted tweet or tweet not visible to you

* 386 -> Too many attachments types (ie a GIF + quote tweet)


Streaming API
=============

Everything is going to be compatibility mode for now; however **all** tweets with have an ``extended_tweet`` node, which will contain the new information. According to Twitter's documentation though, there's the possibility that this node may not exist. We should be careful about making assumptions here.


Changes to Models
=================

Classic tweet: tweet with length < 140 char.
Extended tweet: tweet with extended entities and text > 140 chars.

Twitter doesn't say if extended tweet with a total length of < 140 characters will be considered a "Classic tweet". They also state that an extended tweet shall have "text content [that] exceeds 140 characters in length", however this is contradictory to earlier statements about total text length retaining a hard max at 140 characters.

There will be two rendering modes: Compatibility and Extended. If in compatibility mode and tweet is "classic", no changes to tweet JSON. If in Extended mode, the following will change:

* ``text`` -> truncated version of the extended tweet's text + "..." + permalink to tweet. (Twitter is mute on whether an extended tweet's with (text + @mentions + urls) < 140 characters will have the @mentions + urls put back in ``text`` field.)

* ``truncated`` -> gets set to ``True`` if extended tweet is rendered in compat mode.
