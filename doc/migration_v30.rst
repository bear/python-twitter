Changes to Existing Methods
===========================

GetFollowers():
* Method no longer honors a `count` or `cursor` parameter. These have been deprecated in favor of making this method explicitly a convenience function to return a list of every `twitter.User` who is following the specified or authenticated user. A warning will be raised if `count` or `cursor` is passed with the expectation that breaking behavior will be introduced in a later version.
* Method now takes an optional parameter of `total_count`, which limits the number of users to return. If this is not set, the data returned will be all users following the specified user.
* The kwarg `include_user_entities` now defaults to True. This was set to False previously, but would not be included in query parameters sent to Twitter. Without the query parameter in the URL, Twitter would default to returning user_entities, so this change makes this behavior explicit.

GetFriends():
* Method no longer honors a `count` or `cursor` parameter. These have been deprecated in favor of making this method explicitly a convenience function to return a list of every `twitter.User` who is followed by the specified or authenticated user. A warning will be raised if `count` or `cursor` is passed with the expectation that breaking behavior will be introduced in a later version.
* Method now takes an optional parameter of `total_count`, which limits the number of users to return. If this is not set, the data returned will be all users followed by the specified user.
* The kwarg `include_user_entities` now defaults to True. This was set to False previously, but would not be included in query parameters sent to Twitter. Without the query parameter in the URL, Twitter would default to returning user_entities, so this change makes this behavior explicit.

GetFriendsPaged():
* The third value of the tuple returned by this method is now a list of twitter.User objects in accordance with its doc string rather than the raw data from API. Closes #277
* The kwarg `include_user_entities` now defaults to True. This was set to False previously, but would not be included in query parameters sent to Twitter. Without the query parameter in the URL, Twitter would default to returning user_entities, so this change makes this behavior explicit.

GetFollowersPaged():
* The third value of the tuple returned by this method is now a list of twitter.User objects in accordance with its doc string rather than the raw data from API. Closes #277
* The kwarg `include_user_entities` now defaults to True. This was set to False previously, but would not be included in query parameters sent to Twitter. Without the query parameter in the URL, Twitter would default to returning user_entities, so this change makes this behavior explicit and consistent with the previously ambiguous behavior.

GetSearch():
* You can now specify a user for whom you wish to limit the search. For example, to only get tweets from the user `twitterapi`, you can call `GetSearch(who='twitterapi')` and only that account's tweets will be returned.

GetUserStream():
* Parameter 'stall_warning' is now 'stall_warnings' in line with GetStreamFilter and Twitter's naming convention. This should now actually return stall warnings, whereas it did not have any effect previously.


Deprecation
===========

PostMedia():
* This endpoint is deprecated by Twitter. Python-twitter will throw a warning about using the method and advise you to use PostUpdate() instead. There is no schedule for when this will be removed from Twitter.


New Methods
===========

UploadMediaChunked():
* API method allows chunked upload to upload.twitter.com. Similar to Api.PostMedia(), this method can take either a local filename (str), a URL (str), or a file-like object. The image or video type will be determined by `mimetypes` (see twitter/twitter_utils.py for details).
* Optionally, you can specify a chunk_size for uploads when instantiating the Api object. This should be given in bytes. The default is 1MB (that is, 1048576 bytes). Any chunk_size given below 16KB will result in a warning: Twitter will return an error if you try to upload more than 999 chunks of data; for example, if you are uploading a 15MB video, then a chunk_size lower than 15729 bytes will result in 1000 APPEND commands being sent to the API, so you'll get an error. 16KB seems like a reasonable lower bound, but if your use case is well-defined, then python-twitter will not enforce this behavior.
* Another thing to take into consideration: if you're working in a RAM-constrained environment, a very large chunk_size will increase your RAM usage when uploading media through this endpoint.
* The return value will be the media_id of the uploaded file.

UploadMediaSimple():
* Provides the ability to upload a single media file to Twitter without using the ChunkedUpload endpoint. This method should be used on smaller files and reduces the roundtrips from Twitter from three (for UploadMediaChunked) to one.
* Return value is the `media_id` of the uploaded file.