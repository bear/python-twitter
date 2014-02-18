#!/usr/bin/env python

#
# vim: sw=2 ts=2 sts=2
#
# Copyright 2007 The Python-Twitter Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''A library that provides a Python interface to the Twitter API'''

import base64
from calendar import timegm
import time
import datetime
import gzip
import sys
import textwrap
import types
import urllib
import urllib2
import urlparse
import requests
from requests_oauthlib import OAuth1
import StringIO

from twitter import (__version__, _FileCache, simplejson, DirectMessage, List,
                     Status, Trend, TwitterError, User)

CHARACTER_LIMIT = 140

# A singleton representing a lazily instantiated FileCache.
DEFAULT_CACHE = object()

class Api(object):
  '''A python interface into the Twitter API

  By default, the Api caches results for 1 minute.

  Example usage:

    To create an instance of the twitter.Api class, with no authentication:

      >>> import twitter
      >>> api = twitter.Api()

    To fetch a single user's public status messages, where "user" is either
    a Twitter "short name" or their user id.

      >>> statuses = api.GetUserTimeline(user)
      >>> print [s.text for s in statuses]

    To use authentication, instantiate the twitter.Api class with a
    consumer key and secret; and the oAuth key and secret:

      >>> api = twitter.Api(consumer_key='twitter consumer key',
                            consumer_secret='twitter consumer secret',
                            access_token_key='the_key_given',
                            access_token_secret='the_key_secret')

    To fetch your friends (after being authenticated):

      >>> users = api.GetFriends()
      >>> print [u.name for u in users]

    To post a twitter status message (after being authenticated):

      >>> status = api.PostUpdate('I love python-twitter!')
      >>> print status.text
      I love python-twitter!

    There are many other methods, including:

      >>> api.PostUpdates(status)
      >>> api.PostDirectMessage(user, text)
      >>> api.GetUser(user)
      >>> api.GetReplies()
      >>> api.GetUserTimeline(user)
      >>> api.GetHomeTimeLine()
      >>> api.GetStatus(id)
      >>> api.DestroyStatus(id)
      >>> api.GetFriends(user)
      >>> api.GetFollowers()
      >>> api.GetFeatured()
      >>> api.GetDirectMessages()
      >>> api.GetSentDirectMessages()
      >>> api.PostDirectMessage(user, text)
      >>> api.DestroyDirectMessage(id)
      >>> api.DestroyFriendship(user)
      >>> api.CreateFriendship(user)
      >>> api.LookupFriendship(user)
      >>> api.GetUserByEmail(email)
      >>> api.VerifyCredentials()
  '''

  DEFAULT_CACHE_TIMEOUT = 60  # cache for 1 minute
  _API_REALM = 'Twitter API'

  def __init__(self,
               consumer_key=None,
               consumer_secret=None,
               access_token_key=None,
               access_token_secret=None,
               input_encoding=None,
               request_headers=None,
               cache=DEFAULT_CACHE,
               shortner=None,
               base_url=None,
               stream_url=None,
               use_gzip_compression=False,
               debugHTTP=False,
               requests_timeout=None):
    '''Instantiate a new twitter.Api object.

    Args:
      consumer_key:
        Your Twitter user's consumer_key.
      consumer_secret:
        Your Twitter user's consumer_secret.
      access_token_key:
        The oAuth access token key value you retrieved
        from running get_access_token.py.
      access_token_secret:
        The oAuth access token's secret, also retrieved
        from the get_access_token.py run.
      input_encoding:
        The encoding used to encode input strings. [Optional]
      request_header:
        A dictionary of additional HTTP request headers. [Optional]
      cache:
        The cache instance to use. Defaults to DEFAULT_CACHE.
        Use None to disable caching. [Optional]
      shortner:
        The shortner instance to use.  Defaults to None.
        See shorten_url.py for an example shortner. [Optional]
      base_url:
        The base URL to use to contact the Twitter API.
        Defaults to https://api.twitter.com. [Optional]
      use_gzip_compression:
        Set to True to tell enable gzip compression for any call
        made to Twitter.  Defaults to False. [Optional]
      debugHTTP:
        Set to True to enable debug output from urllib2 when performing
        any HTTP requests.  Defaults to False. [Optional]
      requests_timeout:
        Set timeout (in seconds) of the http/https requests. If None the
        requests lib default will be used.  Defaults to None. [Optional]
    '''
    self.SetCache(cache)
    self._urllib         = urllib2
    self._cache_timeout  = Api.DEFAULT_CACHE_TIMEOUT
    self._input_encoding = input_encoding
    self._use_gzip       = use_gzip_compression
    self._debugHTTP      = debugHTTP
    self._shortlink_size = 19
    self._requests_timeout = requests_timeout

    self._InitializeRequestHeaders(request_headers)
    self._InitializeUserAgent()
    self._InitializeDefaultParameters()

    if base_url is None:
      self.base_url = 'https://api.twitter.com/1.1'
    else:
      self.base_url = base_url
      
    if stream_url is None:
      self.stream_url = 'https://stream.twitter.com/1.1'
    else:
      self.stream_url = stream_url

    if consumer_key is not None and (access_token_key is None or
                                     access_token_secret is None):
      print >> sys.stderr, 'Twitter now requires an oAuth Access Token for API calls.'
      print >> sys.stderr, 'If your using this library from a command line utility, please'
      print >> sys.stderr, 'run the included get_access_token.py tool to generate one.'

      raise TwitterError('Twitter requires oAuth Access Token for all API access')

    self.SetCredentials(consumer_key, consumer_secret, access_token_key, access_token_secret)

    if debugHTTP:
      import logging
      import httplib
      httplib.HTTPConnection.debuglevel = 1

      logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
      logging.getLogger().setLevel(logging.DEBUG)
      requests_log = logging.getLogger("requests.packages.urllib3")
      requests_log.setLevel(logging.DEBUG)
      requests_log.propagate = True

  def SetCredentials(self,
                     consumer_key,
                     consumer_secret,
                     access_token_key=None,
                     access_token_secret=None):
    '''Set the consumer_key and consumer_secret for this instance

    Args:
      consumer_key:
        The consumer_key of the twitter account.
      consumer_secret:
        The consumer_secret for the twitter account.
      access_token_key:
        The oAuth access token key value you retrieved
        from running get_access_token.py.
      access_token_secret:
        The oAuth access token's secret, also retrieved
        from the get_access_token.py run.
    '''
    self._consumer_key        = consumer_key
    self._consumer_secret     = consumer_secret
    self._access_token_key    = access_token_key
    self._access_token_secret = access_token_secret
    auth_list = [consumer_key, consumer_secret,
                 access_token_key, access_token_secret]

    if all(auth_list):
      self.__auth = OAuth1(consumer_key, consumer_secret,  
              access_token_key, access_token_secret)

    self._config = None

  def GetHelpConfiguration(self):
    if self._config is None:
      url  = '%s/help/configuration.json' % self.base_url
      json = self._RequestUrl(url, 'GET')
      data = self._ParseAndCheckTwitter(json.content)
      self._config = data
    return self._config

  def GetShortUrlLength(self, https=False):
    config = self.GetHelpConfiguration()
    if https:
      return config['short_url_length_https']
    else:
      return config['short_url_length']

  def ClearCredentials(self):
    '''Clear the any credentials for this instance
    '''
    self._consumer_key        = None
    self._consumer_secret     = None
    self._access_token_key    = None
    self._access_token_secret = None
    self.__auth               = None  # for request upgrade

  def GetSearch(self,
                term=None,
                geocode=None,
                since_id=None,
                max_id=None,
                until=None,
                count=15,
                lang=None,
                locale=None,
                result_type="mixed",
                include_entities=None):
    '''Return twitter search results for a given term.

    Args:
      term:
        Term to search by. Optional if you include geocode.
      since_id:
        Returns results with an ID greater than (that is, more recent
        than) the specified ID. There are limits to the number of
        Tweets which can be accessed through the API. If the limit of
        Tweets has occurred since the since_id, the since_id will be
        forced to the oldest ID available. [Optional]
      max_id:
        Returns only statuses with an ID less than (that is, older
        than) or equal to the specified ID. [Optional]
      until:
        Returns tweets generated before the given date. Date should be
        formatted as YYYY-MM-DD. [Optional]
      geocode:
        Geolocation information in the form (latitude, longitude, radius)
        [Optional]
      count:
        Number of results to return.  Default is 15 [Optional]
      lang:
        Language for results as ISO 639-1 code.  Default is None (all languages)
        [Optional]
      locale:
        Language of the search query. Currently only 'ja' is effective. This is
        intended for language-specific consumers and the default should work in
        the majority of cases.
      result_type:
        Type of result which should be returned.  Default is "mixed".  Other
        valid options are "recent" and "popular". [Optional]
      include_entities:
        If True, each tweet will include a node called "entities,".
        This node offers a variety of metadata about the tweet in a
        discrete structure, including: user_mentions, urls, and
        hashtags. [Optional]

    Returns:
      A sequence of twitter.Status instances, one for each message containing
      the term
    '''
    # Build request parameters
    parameters = {}

    if since_id:
      try:
        parameters['since_id'] = long(since_id)
      except ValueError:
        raise TwitterError("since_id must be an integer")

    if max_id:
      try:
        parameters['max_id'] = long(max_id)
      except ValueError:
        raise TwitterError("max_id must be an integer")

    if until:
        parameters['until'] = until

    if lang:
      parameters['lang'] = lang

    if locale:
      parameters['locale'] = locale

    if term is None and geocode is None:
      return []

    if term is not None:
      parameters['q'] = term

    if geocode is not None:
      parameters['geocode'] = ','.join(map(str, geocode))

    if include_entities:
      parameters['include_entities'] = 1

    try:
        parameters['count'] = int(count)
    except ValueError:
        raise TwitterError("count must be an integer")

    if result_type in ["mixed", "popular", "recent"]:
      parameters['result_type'] = result_type

    # Make and send requests
    url  = '%s/search/tweets.json' % self.base_url
    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)

    # Return built list of statuses
    return [Status.NewFromJsonDict(x) for x in data['statuses']]

  def GetUsersSearch(self,
                     term=None,
                     page=1,
                     count=20,
                     include_entities=None):
    '''Return twitter user search results for a given term.

    Args:
      term:
        Term to search by.
      page:
        Page of results to return. Default is 1
        [Optional]
      count:
        Number of results to return.  Default is 20
        [Optional]
      include_entities:
        If True, each tweet will include a node called "entities,".
        This node offers a variety of metadata about the tweet in a
        discrete structure, including: user_mentions, urls, and hashtags.
        [Optional]

    Returns:
      A sequence of twitter.User instances, one for each message containing
      the term
    '''
    # Build request parameters
    parameters = {}

    if term is not None:
      parameters['q'] = term

    if page != 1:
      parameters['page'] = page

    if include_entities:
      parameters['include_entities'] = 1

    try:
      parameters['count'] = int(count)
    except ValueError:
      raise TwitterError("count must be an integer")

    # Make and send requests
    url  = '%s/users/search.json' % self.base_url
    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    return [User.NewFromJsonDict(x) for x in data]

  def GetTrendsCurrent(self, exclude=None):
    '''Get the current top trending topics (global)

    Args:
      exclude:
        Appends the exclude parameter as a request parameter.
        Currently only exclude=hashtags is supported. [Optional]

    Returns:
      A list with 10 entries. Each entry contains a trend.
    '''
    return self.GetTrendsWoeid(id=1, exclude=exclude)

  def GetTrendsWoeid(self, id, exclude=None):
    '''Return the top 10 trending topics for a specific WOEID, if trending
    information is available for it.

    Args:
      woeid:
        the Yahoo! Where On Earth ID for a location.
      exclude:
        Appends the exclude parameter as a request parameter.
        Currently only exclude=hashtags is supported. [Optional]

    Returns:
      A list with 10 entries. Each entry contains a trend.
    '''
    url = '%s/trends/place.json' % (self.base_url)
    parameters = {'id': id}

    if exclude:
      parameters['exclude'] = exclude

    json = self._RequestUrl(url, verb='GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)

    trends = []
    timestamp = data[0]['as_of']

    for trend in data[0]['trends']:
        trends.append(Trend.NewFromJsonDict(trend, timestamp=timestamp))
    return trends

  def GetHomeTimeline(self,
                         count=None,
                         since_id=None,
                         max_id=None,
                         trim_user=False,
                         exclude_replies=False,
                         contributor_details=False,
                         include_entities=True):
    '''
    Fetch a collection of the most recent Tweets and retweets posted by the
    authenticating user and the users they follow.

    The home timeline is central to how most users interact with the Twitter
    service.

    The twitter.Api instance must be authenticated.

    Args:
      count:
        Specifies the number of statuses to retrieve. May not be
        greater than 200. Defaults to 20. [Optional]
      since_id:
        Returns results with an ID greater than (that is, more recent
        than) the specified ID. There are limits to the number of
        Tweets which can be accessed through the API. If the limit of
        Tweets has occurred since the since_id, the since_id will be
        forced to the oldest ID available. [Optional]
      max_id:
        Returns results with an ID less than (that is, older than) or
        equal to the specified ID. [Optional]
      trim_user:
        When True, each tweet returned in a timeline will include a user
        object including only the status authors numerical ID. Omit this
        parameter to receive the complete user object. [Optional]
      exclude_replies:
        This parameter will prevent replies from appearing in the
        returned timeline. Using exclude_replies with the count
        parameter will mean you will receive up-to count tweets -
        this is because the count parameter retrieves that many
        tweets before filtering out retweets and replies.
        [Optional]
      contributor_details:
        This parameter enhances the contributors element of the
        status response to include the screen_name of the contributor.
        By default only the user_id of the contributor is included.
        [Optional]
      include_entities:
        The entities node will be disincluded when set to false.
        This node offers a variety of metadata about the tweet in a
        discreet structure, including: user_mentions, urls, and
        hashtags. [Optional]

    Returns:
      A sequence of twitter.Status instances, one for each message
    '''
    url = '%s/statuses/home_timeline.json' % self.base_url

    if not self.__auth:
      raise TwitterError("API must be authenticated.")
    parameters = {}
    if count is not None:
      try:
        if int(count) > 200:
          raise TwitterError("'count' may not be greater than 200")
      except ValueError:
        raise TwitterError("'count' must be an integer")
      parameters['count'] = count
    if since_id:
      try:
        parameters['since_id'] = long(since_id)
      except ValueError:
        raise TwitterError("'since_id' must be an integer")
    if max_id:
      try:
        parameters['max_id'] = long(max_id)
      except ValueError:
        raise TwitterError("'max_id' must be an integer")
    if trim_user:
      parameters['trim_user'] = 1
    if exclude_replies:
      parameters['exclude_replies'] = 1
    if contributor_details:
      parameters['contributor_details'] = 1
    if not include_entities:
      parameters['include_entities'] = 'false'
    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)

    return [Status.NewFromJsonDict(x) for x in data]

  def GetUserTimeline(self,
                      user_id=None,
                      screen_name=None,
                      since_id=None,
                      max_id=None,
                      count=None,
                      include_rts=True,
                      trim_user=None,
                      exclude_replies=None):
    '''Fetch the sequence of public Status messages for a single user.

    The twitter.Api instance must be authenticated if the user is private.

    Args:
      user_id:
        Specifies the ID of the user for whom to return the
        user_timeline. Helpful for disambiguating when a valid user ID
        is also a valid screen name. [Optional]
      screen_name:
        Specifies the screen name of the user for whom to return the
        user_timeline. Helpful for disambiguating when a valid screen
        name is also a user ID. [Optional]
      since_id:
        Returns results with an ID greater than (that is, more recent
        than) the specified ID. There are limits to the number of
        Tweets which can be accessed through the API. If the limit of
        Tweets has occurred since the since_id, the since_id will be
        forced to the oldest ID available. [Optional]
      max_id:
        Returns only statuses with an ID less than (that is, older
        than) or equal to the specified ID. [Optional]
      count:
        Specifies the number of statuses to retrieve. May not be
        greater than 200.  [Optional]
      include_rts:
        If True, the timeline will contain native retweets (if they
        exist) in addition to the standard stream of tweets. [Optional]
      trim_user:
        If True, statuses will only contain the numerical user ID only.
        Otherwise a full user object will be returned for each status.
        [Optional]
      exclude_replies:
        If True, this will prevent replies from appearing in the returned
        timeline. Using exclude_replies with the count parameter will mean you
        will receive up-to count tweets - this is because the count parameter
        retrieves that many tweets before filtering out retweets and replies.
        This parameter is only supported for JSON and XML responses. [Optional]

    Returns:
      A sequence of Status instances, one for each message up to count
    '''
    parameters = {}

    url = '%s/statuses/user_timeline.json' % (self.base_url)

    if user_id:
      parameters['user_id'] = user_id
    elif screen_name:
      parameters['screen_name'] = screen_name

    if since_id:
      try:
        parameters['since_id'] = long(since_id)
      except ValueError:
        raise TwitterError("since_id must be an integer")

    if max_id:
      try:
        parameters['max_id'] = long(max_id)
      except ValueError:
        raise TwitterError("max_id must be an integer")

    if count:
      try:
        parameters['count'] = int(count)
      except ValueError:
        raise TwitterError("count must be an integer")

    if not include_rts:
      parameters['include_rts'] = 0

    if trim_user:
      parameters['trim_user'] = 1

    if exclude_replies:
      parameters['exclude_replies'] = 1

    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    return [Status.NewFromJsonDict(x) for x in data]

  def GetStatus(self,
                id,
                trim_user=False,
                include_my_retweet=True,
                include_entities=True):
    '''Returns a single status message, specified by the id parameter.

    The twitter.Api instance must be authenticated.

    Args:
      id:
        The numeric ID of the status you are trying to retrieve.
      trim_user:
        When set to True, each tweet returned in a timeline will include
        a user object including only the status authors numerical ID.
        Omit this parameter to receive the complete user object.
        [Optional]
      include_my_retweet:
        When set to True, any Tweets returned that have been retweeted by
        the authenticating user will include an additional
        current_user_retweet node, containing the ID of the source status
        for the retweet. [Optional]
      include_entities:
        If False, the entities node will be disincluded.
        This node offers a variety of metadata about the tweet in a
        discreet structure, including: user_mentions, urls, and
        hashtags. [Optional]
    Returns:
      A twitter.Status instance representing that status message
    '''
    url = '%s/statuses/show.json' % (self.base_url)

    if not self.__auth:
      raise TwitterError("API must be authenticated.")

    parameters = {}

    try:
      parameters['id'] = long(id)
    except ValueError:
      raise TwitterError("'id' must be an integer.")

    if trim_user:
      parameters['trim_user'] = 1
    if include_my_retweet:
      parameters['include_my_retweet'] = 1
    if not include_entities:
      parameters['include_entities'] = 'none'

    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    return Status.NewFromJsonDict(data)

  def GetStatusOembed(self,
                id=None,
                url=None,
                maxwidth=None,
                hide_media=False,
                hide_thread=False,
                omit_script=False,
                align=None,
                related=None,
                lang=None):
    '''Returns information allowing the creation of an embedded representation of a
    Tweet on third party sites.
    Specify tweet by the id or url parameter.

    The twitter.Api instance must be authenticated.

    Args:
      id:
        The numeric ID of the status you are trying to embed.
      url:
        The url of the status you are trying to embed.
      maxwidth:
        The maximum width in pixels that the embed should be rendered at.
        This value is constrained to be between 250 and 550 pixels. [Optional]
      hide_media:
        Specifies whether the embedded Tweet should automatically expand images. [Optional]
      hide_thread:
        Specifies whether the embedded Tweet should automatically show the original
        message in the case that the embedded Tweet is a reply. [Optional]
      omit_script:
        Specifies whether the embedded Tweet HTML should include a <script>
        element pointing to widgets.js. [Optional]
      align:
        Specifies whether the embedded Tweet should be left aligned, right aligned,
        or centered in the page. [Optional]
      related:
        A comma sperated string of related screen names. [Optional]
      lang:
        Language code for the rendered embed. [Optional]

    Returns:
      A dictionary with the response.
    '''
    request_url  = '%s/statuses/oembed.json' % (self.base_url)

    if not self.__auth:
      raise TwitterError("API must be authenticated.")

    parameters = {}

    if id is not None:
      try:
        parameters['id'] = long(id)
      except ValueError:
        raise TwitterError("'id' must be an integer.")
    elif url is not None:
      parameters['url'] = url
    else:
      raise TwitterError("Must specify either 'id' or 'url'")

    if maxwidth is not None:
       parameters['maxwidth'] = maxwidth
    if hide_media == True:
       parameters['hide_media'] = 'true'
    if hide_thread == True:
       parameters['hide_thread'] = 'true'
    if omit_script == True:
       parameters['omit_script'] = 'true'
    if align is not None:
       if align not in ('left', 'center', 'right', 'none'):
         raise TwitterError("'align' must be 'left', 'center', 'right', or 'none'")
       parameters['align'] = align
    if related:
        if not isinstance(related, str):
          raise TwitterError("'related' should be a string of comma separated screen names")
        parameters['related'] = related
    if lang is not None:
        if not isinstance(lang, str):
          raise TwitterError("'lang' should be string instance")
        parameters['lang'] = lang
    print 'request_url', request_url, parameters
    json = self._RequestUrl(request_url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    return data

  def DestroyStatus(self, id, trim_user=False):
    '''Destroys the status specified by the required ID parameter.

    The twitter.Api instance must be authenticated and the
    authenticating user must be the author of the specified status.

    Args:
      id:
        The numerical ID of the status you're trying to destroy.

    Returns:
      A twitter.Status instance representing the destroyed status message
    '''
    if not self.__auth:
      raise TwitterError("API must be authenticated.")

    try:
      post_data = {'id': long(id)}
    except ValueError:
      raise TwitterError("id must be an integer")
    url = '%s/statuses/destroy/%s.json' % (self.base_url, id)
    if trim_user:
      post_data['trim_user'] = 1
    json = self._RequestUrl(url, 'POST', data=post_data)
    data = self._ParseAndCheckTwitter(json.content)
    return Status.NewFromJsonDict(data)

  @classmethod
  def _calculate_status_length(cls, status, linksize=19):
    dummy_link_replacement = 'https://-%d-chars%s/' % (linksize, '-' * (linksize - 18))
    shortened = ' '.join([x if not (x.startswith('http://') or
                                    x.startswith('https://'))
                            else
                                dummy_link_replacement
                            for x in status.split(' ')])
    return len(shortened)

  def PostUpdate(self, status, in_reply_to_status_id=None, latitude=None, longitude=None, place_id=None, display_coordinates=False, trim_user=False):
    '''Post a twitter status message from the authenticated user.

    The twitter.Api instance must be authenticated.

    https://dev.twitter.com/docs/api/1.1/post/statuses/update

    Args:
      status:
        The message text to be posted.
        Must be less than or equal to 140 characters.
      in_reply_to_status_id:
        The ID of an existing status that the status to be posted is
        in reply to.  This implicitly sets the in_reply_to_user_id
        attribute of the resulting status to the user ID of the
        message being replied to.  Invalid/missing status IDs will be
        ignored. [Optional]
      latitude:
        Latitude coordinate of the tweet in degrees. Will only work
        in conjunction with longitude argument. Both longitude and
        latitude will be ignored by twitter if the user has a false
        geo_enabled setting. [Optional]
      longitude:
        Longitude coordinate of the tweet in degrees. Will only work
        in conjunction with latitude argument. Both longitude and
        latitude will be ignored by twitter if the user has a false
        geo_enabled setting. [Optional]
      place_id:
        A place in the world. These IDs can be retrieved from
        GET geo/reverse_geocode. [Optional]
      display_coordinates:
        Whether or not to put a pin on the exact coordinates a tweet
        has been sent from. [Optional]
      trim_user:
        If True the returned payload will only contain the user IDs,
        otherwise the payload will contain the full user data item.
        [Optional]
    Returns:
      A twitter.Status instance representing the message posted.
    '''
    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")

    url = '%s/statuses/update.json' % self.base_url

    if isinstance(status, unicode) or self._input_encoding is None:
      u_status = status
    else:
      u_status = unicode(status, self._input_encoding)

    # if self._calculate_status_length(u_status, self._shortlink_size) > CHARACTER_LIMIT:
    #  raise TwitterError("Text must be less than or equal to %d characters. "
    #                     "Consider using PostUpdates." % CHARACTER_LIMIT)

    data = {'status': status}
    if in_reply_to_status_id:
      data['in_reply_to_status_id'] = in_reply_to_status_id
    if latitude is not None and longitude is not None:
      data['lat']     = str(latitude)
      data['long']    = str(longitude)
    if place_id is not None:
      data['place_id'] = str(place_id)
    if display_coordinates:
      data['display_coordinates'] = 'true'
    if trim_user:
      data['trim_user'] = 'true'
    json = self._RequestUrl(url, 'POST', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    return Status.NewFromJsonDict(data)

  def PostMedia(self, status, media, possibly_sensitive=None,
                in_reply_to_status_id=None, latitude=None,
                longitude=None, place_id=None,
                display_coordinates=False):
    '''
    Post a twitter status message from the authenticated user with a
    picture attached.

    Args:
      status:
          the text of your update
      media:
          location of media(PNG, JPG, GIF)
      possibly_sensitive:
          set true is content is "advanced"
      in_reply_to_status_id:
          ID of a status that this is in reply to
      lat:
          location in latitude
      long:
          location in longitude
      place_id:
          A place in the world identified by a Twitter place ID
      display_coordinates:
          Set true if you want to display coordinates

      Returns:
          A twitter.Status instance representing the message posted.
    '''
    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")

    url = '%s/statuses/update_with_media.json' % self.base_url

    if isinstance(status, unicode) or self._input_encoding is None:
      u_status = status
    else:
      u_status = unicode(status, self._input_encoding)

    data = {'status': status}
    data['media'] = open(str(media), 'rb').read()
    if possibly_sensitive:
      data['possibly_sensitive'] = 'true'
    if in_reply_to_status_id:
      data['in_reply_to_status_id'] = in_reply_to_status_id
    if latitude is not None and longitude is not None:
      data['lat']  = str(latitude)
      data['long'] = str(longitude)
    if place_id is not None:
      data['place_id'] = str(place_id)
    if display_coordinates:
      data['display_coordinates'] = 'true'
      
    json = self._RequestUrl(url, 'POST', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    return Status.NewFromJsonDict(data)

  def PostUpdates(self, status, continuation=None, **kwargs):
    '''Post one or more twitter status messages from the authenticated user.

    Unlike api.PostUpdate, this method will post multiple status updates
    if the message is longer than 140 characters.

    The twitter.Api instance must be authenticated.

    Args:
      status:
        The message text to be posted.
        May be longer than 140 characters.
      continuation:
        The character string, if any, to be appended to all but the
        last message.  Note that Twitter strips trailing '...' strings
        from messages.  Consider using the unicode \u2026 character
        (horizontal ellipsis) instead. [Defaults to None]
      **kwargs:
        See api.PostUpdate for a list of accepted parameters.

    Returns:
      A of list twitter.Status instance representing the messages posted.
    '''
    results = list()
    if continuation is None:
      continuation = ''
    line_length = CHARACTER_LIMIT - len(continuation)
    lines = textwrap.wrap(status, line_length)
    for line in lines[0:-1]:
      results.append(self.PostUpdate(line + continuation, **kwargs))
    results.append(self.PostUpdate(lines[-1], **kwargs))
    return results

  def PostRetweet(self, original_id, trim_user=False):
    '''Retweet a tweet with the Retweet API.

    The twitter.Api instance must be authenticated.

    Args:
      original_id:
        The numerical id of the tweet that will be retweeted
      trim_user:
        If True the returned payload will only contain the user IDs,
        otherwise the payload will contain the full user data item.
        [Optional]

    Returns:
      A twitter.Status instance representing the original tweet with retweet details embedded.
    '''
    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")

    try:
      if int(original_id) <= 0:
        raise TwitterError("'original_id' must be a positive number")
    except ValueError:
        raise TwitterError("'original_id' must be an integer")

    url = '%s/statuses/retweet/%s.json' % (self.base_url, original_id)

    data = {'id': original_id}
    if trim_user:
      data['trim_user'] = 'true'
    json = self._RequestUrl(url, 'POST', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    return Status.NewFromJsonDict(data)

  def GetUserRetweets(self, count=None, since_id=None, max_id=None, trim_user=False):
    '''Fetch the sequence of retweets made by the authenticated user.

    The twitter.Api instance must be authenticated.

    Args:
      count:
        The number of status messages to retrieve. [Optional]
      since_id:
        Returns results with an ID greater than (that is, more recent
        than) the specified ID. There are limits to the number of
        Tweets which can be accessed through the API. If the limit of
        Tweets has occurred since the since_id, the since_id will be
        forced to the oldest ID available. [Optional]
      max_id:
        Returns results with an ID less than (that is, older than) or
        equal to the specified ID. [Optional]
      trim_user:
        If True the returned payload will only contain the user IDs,
        otherwise the payload will contain the full user data item.
        [Optional]

    Returns:
      A sequence of twitter.Status instances, one for each message up to count
    '''
    return self.GetUserTimeline(since_id=since_id, count=count, max_id=max_id, trim_user=trim_user, exclude_replies=True, include_rts=True)

  def GetReplies(self, since_id=None, count=None, max_id=None, trim_user=False):
    '''Get a sequence of status messages representing the 20 most
    recent replies (status updates prefixed with @twitterID) to the
    authenticating user.

    Args:
      since_id:
        Returns results with an ID greater than (that is, more recent
        than) the specified ID. There are limits to the number of
        Tweets which can be accessed through the API. If the limit of
        Tweets has occurred since the since_id, the since_id will be
        forced to the oldest ID available. [Optional]
      max_id:
        Returns results with an ID less than (that is, older than) or
        equal to the specified ID. [Optional]
      trim_user:
        If True the returned payload will only contain the user IDs,
        otherwise the payload will contain the full user data item.
        [Optional]

    Returns:
      A sequence of twitter.Status instances, one for each reply to the user.
    '''
    return self.GetUserTimeline(since_id=since_id, count=count, max_id=max_id, trim_user=trim_user, exclude_replies=False, include_rts=False)

  def GetRetweets(self, statusid, count=None, trim_user=False):
    '''Returns up to 100 of the first retweets of the tweet identified
    by statusid

    Args:
      statusid:
        The ID of the tweet for which retweets should be searched for
      count:
        The number of status messages to retrieve. [Optional]
      trim_user:
        If True the returned payload will only contain the user IDs,
        otherwise the payload will contain the full user data item.
        [Optional]

    Returns:
      A list of twitter.Status instances, which are retweets of statusid
    '''
    if not self.__auth:
      raise TwitterError("The twitter.Api instsance must be authenticated.")
    url = '%s/statuses/retweets/%s.json' % (self.base_url, statusid)
    parameters = {}
    if trim_user:
      parameters['trim_user'] = 'true'
    if count:
      try:
        parameters['count'] = int(count)
      except ValueError:
        raise TwitterError("count must be an integer")
    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    return [Status.NewFromJsonDict(s) for s in data]

  def GetRetweeters(self, status_id, cursor=None, stringify_ids=None):
    '''Returns a collection of up to 100 user IDs belonging to
    users who have retweeted the tweet specified by the id parameter.

    Args:
      status_id:
        the tweet's numerical ID
      cursor:
        breaks the ids into pages of no more than 100.
        [Semi-Optional]
      stringify_ids:
        returns the IDs as unicode strings [Optional]

    Returns:
      A list of user IDs
    '''
    if not self.__auth:
      raise TwitterError("The twitter.Api instsance must be authenticated.")
    url = '%s/statuses/retweeters/ids.json' % (self.base_url)
    parameters = {}
    parameters['id'] = status_id
    if stringify_ids:
      parameters['stringify_ids'] = 'true'
    result = []
    while True:
      if cursor:
        try:
          parameters['count'] = int(cursor)
        except ValueError:
          raise TwitterError("cursor must be an integer")
          break
      json = self._RequestUrl(url, 'GET', data=parameters)
      data = self._ParseAndCheckTwitter(json.content)
      result += [x for x in data['ids']]
      if 'next_cursor' in data:
        if data['next_cursor'] == 0 or data['next_cursor'] == data['previous_cursor']:
          break
        else:
          cursor = data['next_cursor']
          total_count -= len(data['ids'])
          if total_count < 1:
            break
      else:
        break
    return result

  def GetRetweetsOfMe(self,
                      count=None,
                      since_id=None,
                      max_id=None,
                      trim_user=False,
                      include_entities=True,
                      include_user_entities=True):
    '''Returns up to 100 of the most recent tweets of the user that have been
    retweeted by others.

    Args:
      count:
        The number of retweets to retrieve, up to 100. If omitted, 20 is
        assumed.
      since_id:
        Returns results with an ID greater than (newer than) this ID.
      max_id:
        Returns results with an ID less than or equal to this ID.
      trim_user:
        When True, the user object for each tweet will only be an ID.
      include_entities:
        When True, the tweet entities will be included.
      include_user_entities:
        When True, the user entities will be included.
    '''
    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")
    url = '%s/statuses/retweets_of_me.json' % self.base_url
    parameters = {}
    if count is not None:
      try:
        if int(count) > 100:
          raise TwitterError("'count' may not be greater than 100")
      except ValueError:
        raise TwitterError("'count' must be an integer")
    if count:
      parameters['count'] = count
    if since_id:
      parameters['since_id'] = since_id
    if max_id:
      parameters['max_id'] = max_id
    if trim_user:
      parameters['trim_user'] = trim_user
    if not include_entities:
      parameters['include_entities'] = include_entities
    if not include_user_entities:
      parameters['include_user_entities'] = include_user_entities
    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    return [Status.NewFromJsonDict(s) for s in data]

  def GetBlocks(self, user_id=None, screen_name=None, cursor=-1, skip_status=False, include_user_entities=False):
    '''Fetch the sequence of twitter.User instances, one for each blocked user.

    The twitter.Api instance must be authenticated.

    Args:
      user_id:
        The twitter id of the user whose friends you are fetching.
        If not specified, defaults to the authenticated user. [Optional]
      screen_name:
        The twitter name of the user whose friends you are fetching.
        If not specified, defaults to the authenticated user. [Optional]
      cursor:
        Should be set to -1 for the initial call and then is used to
        control what result page Twitter returns [Optional(ish)]
      skip_status:
        If True the statuses will not be returned in the user items.
        [Optional]
      include_user_entities:
        When True, the user entities will be included.

    Returns:
      A sequence of twitter.User instances, one for each friend
    '''
    if not self.__auth:
      raise TwitterError("twitter.Api instance must be authenticated")
    url = '%s/blocks/list.json' % self.base_url
    result = []
    parameters = {}
    if user_id is not None:
      parameters['user_id'] = user_id
    if screen_name is not None:
      parameters['screen_name'] = screen_name
    if skip_status:
      parameters['skip_status'] = True
    if include_user_entities:
      parameters['include_user_entities'] = True
    while True:
      parameters['cursor'] = cursor
      json = self._RequestUrl(url, 'GET', data=parameters)
      data = self._ParseAndCheckTwitter(json.content)
      result += [User.NewFromJsonDict(x) for x in data['users']]
      if 'next_cursor' in data:
        if data['next_cursor'] == 0 or data['next_cursor'] == data['previous_cursor']:
          break
        else:
          cursor = data['next_cursor']
      else:
        break
    return result

  def GetFriends(self, user_id=None, screen_name=None, cursor=-1, count=None, skip_status=False, include_user_entities=False):
    '''Fetch the sequence of twitter.User instances, one for each friend.

    The twitter.Api instance must be authenticated.

    Args:
      user_id:
        The twitter id of the user whose friends you are fetching.
        If not specified, defaults to the authenticated user. [Optional]
      screen_name:
        The twitter name of the user whose friends you are fetching.
        If not specified, defaults to the authenticated user. [Optional]
      cursor:
        Should be set to -1 for the initial call and then is used to
        control what result page Twitter returns [Optional(ish)]
      count:
        The number of users to return per page, up to a maximum of 200.
        Defaults to 20. [Optional]
      skip_status:
        If True the statuses will not be returned in the user items.
        [Optional]
      include_user_entities:
        When True, the user entities will be included.

    Returns:
      A sequence of twitter.User instances, one for each friend
    '''
    if not self.__auth:
      raise TwitterError("twitter.Api instance must be authenticated")
    url = '%s/friends/list.json' % self.base_url
    result = []
    parameters = {}
    if user_id is not None:
      parameters['user_id'] = user_id
    if screen_name is not None:
      parameters['screen_name'] = screen_name
    if count:
      try:
        parameters['count'] = int(count)
      except ValueError:
        raise TwitterError("count must be an integer")
    if skip_status:
      parameters['skip_status'] = True
    if include_user_entities:
      parameters['include_user_entities'] = True
    while True:
      parameters['cursor'] = cursor
      json = self._RequestUrl(url, 'GET', data=parameters)
      data = self._ParseAndCheckTwitter(json.content)
      result += [User.NewFromJsonDict(x) for x in data['users']]
      if 'next_cursor' in data:
        if data['next_cursor'] == 0 or data['next_cursor'] == data['previous_cursor']:
          break
        else:
          cursor = data['next_cursor']
      else:
        break
      sec = self.GetSleepTime('/friends/list')
      time.sleep(sec)
    return result

  def GetFriendIDs(self, user_id=None, screen_name=None, cursor=-1, stringify_ids=False, count=None):
      '''Returns a list of twitter user id's for every person
      the specified user is following.

      Args:
        user_id:
          The id of the user to retrieve the id list for
          [Optional]
        screen_name:
          The screen_name of the user to retrieve the id list for
          [Optional]
        cursor:
          Specifies the Twitter API Cursor location to start at.
          Note: there are pagination limits.
          [Optional]
        stringify_ids:
          if True then twitter will return the ids as strings instead of integers.
          [Optional]
        count:
          The number of status messages to retrieve. [Optional]

      Returns:
        A list of integers, one for each user id.
      '''
      url = '%s/friends/ids.json' % self.base_url
      if not self.__auth:
          raise TwitterError("twitter.Api instance must be authenticated")
      parameters = {}
      if user_id is not None:
        parameters['user_id'] = user_id
      if screen_name is not None:
        parameters['screen_name'] = screen_name
      if stringify_ids:
        parameters['stringify_ids'] = True
      if count is not None:
        parameters['count'] = count
      result = []
      while True:
        parameters['cursor'] = cursor
        json = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(json.content)
        result += [x for x in data['ids']]
        if 'next_cursor' in data:
          if data['next_cursor'] == 0 or data['next_cursor'] == data['previous_cursor']:
            break
          else:
            cursor = data['next_cursor']
        else:
          break
        sec = self.GetSleepTime('/friends/ids')
        time.sleep(sec)        
      return result


  def GetFollowerIDs(self, user_id=None, screen_name=None, cursor=-1, stringify_ids=False, count=None, total_count=None):
      '''Returns a list of twitter user id's for every person
      that is following the specified user.

      Args:
        user_id:
          The id of the user to retrieve the id list for
          [Optional]
        screen_name:
          The screen_name of the user to retrieve the id list for
          [Optional]
        cursor:
          Specifies the Twitter API Cursor location to start at.
          Note: there are pagination limits.
          [Optional]
        stringify_ids:
          if True then twitter will return the ids as strings instead of integers.
          [Optional]
        count:
          The number of user id's to retrieve per API request. Please be aware that
          this might get you rate-limited if set to a small number. By default Twitter
          will retrieve 5000 UIDs per call.
          [Optional]
        total_count:
          The total amount of UIDs to retrieve. Good if the account has many followers
          and you don't want to get rate limited. The data returned might contain more
          UIDs if total_count is not a multiple of count (5000 by default).
          [Optional]


      Returns:
        A list of integers, one for each user id.
      '''
      url = '%s/followers/ids.json' % self.base_url
      if not self.__auth:
          raise TwitterError("twitter.Api instance must be authenticated")
      parameters = {}
      if user_id is not None:
        parameters['user_id'] = user_id
      if screen_name is not None:
        parameters['screen_name'] = screen_name
      if stringify_ids:
        parameters['stringify_ids'] = True
      if count is not None:
        parameters['count'] = count
      result = []
      while True:
        if total_count and total_count < count:
          parameters['count'] = total_count
        parameters['cursor'] = cursor
        json = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(json.content)
        result += [x for x in data['ids']]
        if 'next_cursor' in data:
          if data['next_cursor'] == 0 or data['next_cursor'] == data['previous_cursor']:
            break
          else:
            cursor = data['next_cursor']
            if total_count is not None:
              total_count -= len(data['ids'])
              if total_count < 1:
                break
        else:
          break
        sec = self.GetSleepTime('/followers/ids')
        time.sleep(sec) 
      return result

  def GetFollowersPaged(self, user_id=None, screen_name=None, cursor=-1, count=200, skip_status=False, include_user_entities=False):
    '''Make a cursor driven call to return the list of all followers

    The caller is responsible for handling the cursor value and looping
    to gather all of the data

    Args:
      user_id:
        The twitter id of the user whose followers you are fetching.
        If not specified, defaults to the authenticated user. [Optional]
      screen_name:
        The twitter name of the user whose followers you are fetching.
        If not specified, defaults to the authenticated user. [Optional]
      cursor:
        Should be set to -1 for the initial call and then is used to
        control what result page Twitter returns [Optional(ish)]
      count:
        The number of users to return per page, up to a maximum of 200.
        Defaults to 200. [Optional]
      skip_status:
        If True the statuses will not be returned in the user items.
        [Optional]
      include_user_entities:
        When True, the user entities will be included.

    Returns:
      next_cursor, previous_cursor, data sequence of twitter.User instances, one for each follower
    '''
    url = '%s/followers/list.json' % self.base_url
    result = []
    parameters = {}
    if user_id is not None:
      parameters['user_id'] = user_id
    if screen_name is not None:
      parameters['screen_name'] = screen_name
    try:
      parameters['count'] = int(count)
    except ValueError:
      raise TwitterError("count must be an integer")
    if skip_status:
      parameters['skip_status'] = True
    if include_user_entities:
      parameters['include_user_entities'] = True
    parameters['cursor'] = cursor
    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    if 'next_cursor' in data:
      next_cursor = data['next_cursor']
    else:
      next_cursor = 0
    if 'previous_cursor' in data:
      previous_cursor = data['previous_cursor']
    else:
      previous_cursor = 0
    return next_cursor, previous_cursor, data

  def GetFollowers(self, user_id=None, screen_name=None, cursor=-1, count=200, skip_status=False, include_user_entities=False):
    '''Fetch the sequence of twitter.User instances, one for each follower

    The twitter.Api instance must be authenticated.

    Args:
      user_id:
        The twitter id of the user whose followers you are fetching.
        If not specified, defaults to the authenticated user. [Optional]
      screen_name:
        The twitter name of the user whose followers you are fetching.
        If not specified, defaults to the authenticated user. [Optional]
      cursor:
        Should be set to -1 for the initial call and then is used to
        control what result page Twitter returns [Optional(ish)]
      count:
        The number of users to return per page, up to a maximum of 200.
        Defaults to 200. [Optional]
      skip_status:
        If True the statuses will not be returned in the user items.
        [Optional]
      include_user_entities:
        When True, the user entities will be included.

    Returns:
      A sequence of twitter.User instances, one for each follower
    '''
    if not self.__auth:
      raise TwitterError("twitter.Api instance must be authenticated")
    result = []
    parameters = {}
    while True:
      next_cursor, previous_cursor, data = self.GetFollowersPaged(user_id, screen_name, cursor, count, skip_status, include_user_entities)
      result += [User.NewFromJsonDict(x) for x in data['users']]
      if next_cursor == 0 or next_cursor == previous_cursor:
        break
      else:
        cursor = next_cursor
      sec = self.GetSleepTime('/followers/list')
      time.sleep(sec) 
    return result

  def UsersLookup(self, user_id=None, screen_name=None, users=None, include_entities=True):
    '''Fetch extended information for the specified users.

    Users may be specified either as lists of either user_ids,
    screen_names, or twitter.User objects. The list of users that
    are queried is the union of all specified parameters.

    The twitter.Api instance must be authenticated.

    Args:
      user_id:
        A list of user_ids to retrieve extended information.
        [Optional]
      screen_name:
        A list of screen_names to retrieve extended information.
        [Optional]
      users:
        A list of twitter.User objects to retrieve extended information.
        [Optional]
      include_entities:
        The entities node that may appear within embedded statuses will be
        disincluded when set to False.
        [Optional]

    Returns:
      A list of twitter.User objects for the requested users
    '''

    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")
    if not user_id and not screen_name and not users:
      raise TwitterError("Specify at least one of user_id, screen_name, or users.")
    url = '%s/users/lookup.json' % self.base_url
    parameters = {}
    uids = list()
    if user_id:
      uids.extend(user_id)
    if users:
      uids.extend([u.id for u in users])
    if len(uids):
      parameters['user_id'] = ','.join(["%s" % u for u in uids])
    if screen_name:
      parameters['screen_name'] = ','.join(screen_name)
    if not include_entities:
      parameters['include_entities'] = 'false'
    json = self._RequestUrl(url, 'GET', data=parameters)
    try:
      data = self._ParseAndCheckTwitter(json.content)
    except TwitterError, e:
        _, e, _ = sys.exc_info()
        t = e.args[0]
        if len(t) == 1 and ('code' in t[0]) and (t[0]['code'] == 34):
          data = []
        else:
            raise

    return [User.NewFromJsonDict(u) for u in data]

  def GetUser(self, user_id=None, screen_name=None, include_entities=True):
    '''Returns a single user.

    The twitter.Api instance must be authenticated.

    Args:
      user_id:
        The id of the user to retrieve.
        [Optional]
      screen_name:
        The screen name of the user for whom to return results for. Either a
        user_id or screen_name is required for this method.
        [Optional]
      include_entities:
        if set to False, the 'entities' node will not be included.
        [Optional]


    Returns:
      A twitter.User instance representing that user
    '''
    url = '%s/users/show.json' % (self.base_url)
    parameters = {}

    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")

    if user_id:
      parameters['user_id'] = user_id
    elif screen_name:
      parameters['screen_name'] = screen_name
    else:
      raise TwitterError("Specify at least one of user_id or screen_name.")

    if not include_entities:
      parameters['include_entities'] = 'false'

    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    return User.NewFromJsonDict(data)

  def GetDirectMessages(self, since_id=None, max_id=None, count=None, include_entities=True, skip_status=False):
    '''Returns a list of the direct messages sent to the authenticating user.

    The twitter.Api instance must be authenticated.

    Args:
      since_id:
        Returns results with an ID greater than (that is, more recent
        than) the specified ID. There are limits to the number of
        Tweets which can be accessed through the API. If the limit of
        Tweets has occurred since the since_id, the since_id will be
        forced to the oldest ID available. [Optional]
      max_id:
        Returns results with an ID less than (that is, older than) or
        equal to the specified ID. [Optional]
      count:
        Specifies the number of direct messages to try and retrieve, up to a
        maximum of 200. The value of count is best thought of as a limit to the
        number of Tweets to return because suspended or deleted content is
        removed after the count has been applied. [Optional]
      include_entities:
        The entities node will not be included when set to False.
        [Optional]
      skip_status:
        When set to True statuses will not be included in the returned user
        objects. [Optional]

    Returns:
      A sequence of twitter.DirectMessage instances
    '''
    url = '%s/direct_messages.json' % self.base_url
    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")
    parameters = {}
    if since_id:
      parameters['since_id'] = since_id
    if max_id:
      parameters['max_id'] = max_id
    if count:
      try:
        parameters['count'] = int(count)
      except ValueError:
        raise TwitterError("count must be an integer")
    if not include_entities:
      parameters['include_entities'] = 'false'
    if skip_status:
      parameters['skip_status'] = 1
    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    return [DirectMessage.NewFromJsonDict(x) for x in data]

  def GetSentDirectMessages(self, since_id=None, max_id=None, count=None, page=None, include_entities=True):
    '''Returns a list of the direct messages sent by the authenticating user.

    The twitter.Api instance must be authenticated.

    Args:
      since_id:
        Returns results with an ID greater than (that is, more recent
        than) the specified ID. There are limits to the number of
        Tweets which can be accessed through the API. If the limit of
        Tweets has occured since the since_id, the since_id will be
        forced to the oldest ID available. [Optional]
      max_id:
        Returns results with an ID less than (that is, older than) or
        equal to the specified ID. [Optional]
      count:
        Specifies the number of direct messages to try and retrieve, up to a
        maximum of 200. The value of count is best thought of as a limit to the
        number of Tweets to return because suspended or deleted content is
        removed after the count has been applied. [Optional]
      page:
        Specifies the page of results to retrieve.
        Note: there are pagination limits. [Optional]
      include_entities:
        The entities node will not be included when set to False.
        [Optional]

    Returns:
      A sequence of twitter.DirectMessage instances
    '''
    url = '%s/direct_messages/sent.json' % self.base_url
    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")
    parameters = {}
    if since_id:
      parameters['since_id'] = since_id
    if page:
      parameters['page'] = page
    if max_id:
      parameters['max_id'] = max_id
    if count:
      try:
        parameters['count'] = int(count)
      except ValueError:
        raise TwitterError("count must be an integer")
    if not include_entities:
      parameters['include_entities'] = 'false'
    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    return [DirectMessage.NewFromJsonDict(x) for x in data]

  def PostDirectMessage(self, text, user_id=None, screen_name=None):
    '''Post a twitter direct message from the authenticated user

    The twitter.Api instance must be authenticated. user_id or screen_name
    must be specified.

    Args:
      text: The message text to be posted.  Must be less than 140 characters.
      user_id:
        The ID of the user who should receive the direct message.
        [Optional]
      screen_name:
        The screen name of the user who should receive the direct message.
        [Optional]

    Returns:
      A twitter.DirectMessage instance representing the message posted
    '''
    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")
    url = '%s/direct_messages/new.json' % self.base_url
    data = {'text': text}
    if user_id:
      data['user_id'] = user_id
    elif screen_name:
      data['screen_name'] = screen_name
    else:
      raise TwitterError("Specify at least one of user_id or screen_name.")
    json = self._RequestUrl(url, 'POST', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    return DirectMessage.NewFromJsonDict(data)

  def DestroyDirectMessage(self, id, include_entities=True):
    '''Destroys the direct message specified in the required ID parameter.

    The twitter.Api instance must be authenticated, and the
    authenticating user must be the recipient of the specified direct
    message.

    Args:
      id: The id of the direct message to be destroyed

    Returns:
      A twitter.DirectMessage instance representing the message destroyed
    '''
    url = '%s/direct_messages/destroy.json' % self.base_url
    data = {'id': id}
    if not include_entities:
      data['include_entities'] = 'false'
    json = self._RequestUrl(url, 'POST', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    return DirectMessage.NewFromJsonDict(data)

  def CreateFriendship(self, user_id=None, screen_name=None, follow=True):
    '''Befriends the user specified by the user_id or screen_name.

    The twitter.Api instance must be authenticated.

    Args:
      user_id:
        A user_id to follow [Optional]
      screen_name:
        A screen_name to follow [Optional]
      follow:
        Set to False to disable notifications for the target user
    Returns:
      A twitter.User instance representing the befriended user.
    '''
    url = '%s/friendships/create.json' % (self.base_url)
    data = {}
    if user_id:
      data['user_id'] = user_id
    elif screen_name:
      data['screen_name'] = screen_name
    else:
      raise TwitterError("Specify at least one of user_id or screen_name.")
    if follow:
      data['follow'] = 'true'
    else:
      data['follow'] = 'false'
    json = self._RequestUrl(url, 'POST', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    return User.NewFromJsonDict(data)

  def DestroyFriendship(self, user_id=None, screen_name=None):
    '''Discontinues friendship with a user_id or screen_name.

    The twitter.Api instance must be authenticated.

    Args:
      user_id:
        A user_id to unfollow [Optional]
      screen_name:
        A screen_name to unfollow [Optional]
    Returns:
      A twitter.User instance representing the discontinued friend.
    '''
    url = '%s/friendships/destroy.json' % self.base_url
    data = {}
    if user_id:
      data['user_id'] = user_id
    elif screen_name:
      data['screen_name'] = screen_name
    else:
      raise TwitterError("Specify at least one of user_id or screen_name.")
    json = self._RequestUrl(url, 'POST', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    return User.NewFromJsonDict(data)

  def LookupFriendship(self, user_id=None, screen_name=None):
    '''Lookup friendship status for user specified by user_id or screen_name.
    Currently only supports one user at a time.

    The twitter.Api instance must be authenticated.

    Args:
      user_id:
        A user_id to lookup [Optional]
      screen_name:
        A screen_name to lookup [Optional]
    Returns:
      A twitter.UserStatus instance representing the friendship status
    '''
    url = '%s/friendships/lookup.json' % (self.base_url)
    data = {}
    if user_id:
      data['user_id'] = user_id
    elif screen_name:
      data['screen_name'] = screen_name
    else:
      raise TwitterError("Specify at least one of user_id or screen_name.")
    json = self._RequestUrl(url, 'GET', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    if len(data) >= 1:
      return UserStatus.NewFromJsonDict(data[0])
    else:
      return None

  def CreateFavorite(self, status=None, id=None, include_entities=True):
    '''Favorites the specified status object or id as the authenticating user.
    Returns the favorite status when successful.

    The twitter.Api instance must be authenticated.

    Args:
      id:
        The id of the twitter status to mark as a favorite.
        [Optional]
      status:
        The twitter.Status object to mark as a favorite.
        [Optional]
      include_entities:
        The entities node will be omitted when set to False.
    Returns:
      A twitter.Status instance representing the newly-marked favorite.
    '''
    url = '%s/favorites/create.json' % self.base_url
    data = {}
    if id:
      data['id'] = id
    elif status:
      data['id'] = status.id
    else:
      raise TwitterError("Specify id or status")
    if not include_entities:
      data['include_entities'] = 'false'
    json = self._RequestUrl(url, 'POST', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    return Status.NewFromJsonDict(data)

  def DestroyFavorite(self, status=None, id=None, include_entities=True):
    '''Un-Favorites the specified status object or id as the authenticating user.
    Returns the un-favorited status when successful.

    The twitter.Api instance must be authenticated.

    Args:
      id:
        The id of the twitter status to unmark as a favorite.
        [Optional]
      status:
        The twitter.Status object to unmark as a favorite.
        [Optional]
      include_entities:
        The entities node will be omitted when set to False.
    Returns:
      A twitter.Status instance representing the newly-unmarked favorite.
    '''
    url = '%s/favorites/destroy.json' % self.base_url
    data = {}
    if id:
      data['id'] = id
    elif status:
      data['id'] = status.id
    else:
      raise TwitterError("Specify id or status")
    if not include_entities:
      data['include_entities'] = 'false'
    json = self._RequestUrl(url, 'POST', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    return Status.NewFromJsonDict(data)

  def GetFavorites(self,
                   user_id=None,
                   screen_name=None,
                   count=None,
                   since_id=None,
                   max_id=None,
                   include_entities=True):
    '''Return a list of Status objects representing favorited tweets.
    By default, returns the (up to) 20 most recent tweets for the
    authenticated user.

    Args:
      user:
        The twitter name or id of the user whose favorites you are fetching.
        If not specified, defaults to the authenticated user. [Optional]
      page:
        Specifies the page of results to retrieve.
        Note: there are pagination limits. [Optional]
    '''
    parameters = {}

    url = '%s/favorites/list.json' % self.base_url

    if user_id:
      parameters['user_id'] = user_id
    elif screen_name:
      parameters['screen_name'] = screen_name

    if since_id:
      try:
        parameters['since_id'] = long(since_id)
      except ValueError:
        raise TwitterError("since_id must be an integer")

    if max_id:
      try:
        parameters['max_id'] = long(max_id)
      except ValueError:
        raise TwitterError("max_id must be an integer")

    if count:
      try:
        parameters['count'] = int(count)
      except ValueError:
        raise TwitterError("count must be an integer")

    if include_entities:
        parameters['include_entities'] = True


    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    return [Status.NewFromJsonDict(x) for x in data]

  def GetMentions(self,
                  count=None,
                  since_id=None,
                  max_id=None,
                  trim_user=False,
                  contributor_details=False,
                  include_entities=True):
    '''Returns the 20 most recent mentions (status containing @screen_name)
    for the authenticating user.

    Args:
      count:
        Specifies the number of tweets to try and retrieve, up to a maximum of
        200. The value of count is best thought of as a limit to the number of
        tweets to return because suspended or deleted content is removed after
        the count has been applied. [Optional]
      since_id:
        Returns results with an ID greater than (that is, more recent
        than) the specified ID. There are limits to the number of
        Tweets which can be accessed through the API. If the limit of
        Tweets has occurred since the since_id, the since_id will be
        forced to the oldest ID available. [Optional]
      max_id:
        Returns only statuses with an ID less than
        (that is, older than) the specified ID.  [Optional]
      trim_user:
        When set to True, each tweet returned in a timeline will include a user
        object including only the status authors numerical ID. Omit this
        parameter to receive the complete user object.
      contributor_details:
        If set to True, this parameter enhances the contributors element of the
        status response to include the screen_name of the contributor. By
        default only the user_id of the contributor is included.
      include_entities:
        The entities node will be disincluded when set to False.

    Returns:
      A sequence of twitter.Status instances, one for each mention of the user.
    '''

    url = '%s/statuses/mentions_timeline.json' % self.base_url

    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")

    parameters = {}

    if count:
      try:
        parameters['count'] = int(count)
      except ValueError:
        raise TwitterError("count must be an integer")
    if since_id:
      try:
        parameters['since_id'] = long(since_id)
      except ValueError:
        raise TwitterError("since_id must be an integer")
    if max_id:
      try:
        parameters['max_id'] = long(max_id)
      except ValueError:
        raise TwitterError("max_id must be an integer")
    if trim_user:
      parameters['trim_user'] = 1
    if contributor_details:
      parameters['contributor_details'] = 'true'
    if not include_entities:
      parameters['include_entities'] = 'false'

    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    return [Status.NewFromJsonDict(x) for x in data]


  # List endpoint status
  # done GET lists/list
  # done GET lists/statuses
  # done POST lists/subscribers/create
  # done GET lists/subscribers/show
  # done POST lists/subscribers/destroy
  # done GET lists/members
  # done POST lists/members/create
  # done POST lists/members/create_all
  # done POST lists/members/destroy
  # done POST lists/members/destroy_all
  #      GET lists/members/show
  # done POST lists/create
  # done POST lists/destroy
  #      POST lists/update
  #      GET lists/show
  # done GET lists/subscriptions
  #      GET lists/memberships
  #      GET lists/subscribers
  # done GET lists/ownerships

  def CreateList(self, name, mode=None, description=None):
    '''Creates a new list with the give name for the authenticated user.

    The twitter.Api instance must be authenticated.

    Twitter endpoint: /lists/create

    Args:
      name:
        New name for the list
      mode:
        'public' or 'private'.
        Defaults to 'public'. [Optional]
      description:
        Description of the list. [Optional]

    Returns:
      A twitter.List instance representing the new list
    '''
    url = '%s/lists/create.json' % self.base_url

    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")
    parameters = {'name': name}
    if mode is not None:
      parameters['mode'] = mode
    if description is not None:
      parameters['description'] = description
    json = self._RequestUrl(url, 'POST', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    return List.NewFromJsonDict(data)

  def DestroyList(self,
                  owner_screen_name=False,
                  owner_id=False,
                  list_id=None,
                  slug=None):
    '''
    Destroys the list identified by list_id or owner_screen_name/owner_id and
    slug.

    The twitter.Api instance must be authenticated.

    Twitter endpoint: /lists/destroy

    Args:
      owner_screen_name:
        The screen_name of the user who owns the list being requested by a slug.
      owner_id:
        The user ID of the user who owns the list being requested by a slug.
      list_id:
        The numerical id of the list.
      slug:
        You can identify a list by its slug instead of its numerical id. If you
        decide to do so, note that you'll also have to specify the list owner
        using the owner_id or owner_screen_name parameters.
    Returns:
      A twitter.List instance representing the removed list.
    '''
    url = '%s/lists/destroy.json' % self.base_url
    data = {}
    if list_id:
      try:
        data['list_id'] = long(list_id)
      except ValueError:
        raise TwitterError("list_id must be an integer")
    elif slug:
      data['slug'] = slug
      if owner_id:
        try:
          data['owner_id'] = long(owner_id)
        except ValueError:
          raise TwitterError("owner_id must be an integer")
      elif owner_screen_name:
        data['owner_screen_name'] = owner_screen_name
      else:
        raise TwitterError("Identify list by list_id or owner_screen_name/owner_id and slug")
    else:
      raise TwitterError("Identify list by list_id or owner_screen_name/owner_id and slug")

    json = self._RequestUrl(url, 'POST', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    return List.NewFromJsonDict(data)

  def CreateSubscription(self,
                         owner_screen_name=False,
                         owner_id=False,
                         list_id=None,
                         slug=None):
    '''Creates a subscription to a list by the authenticated user

    The twitter.Api instance must be authenticated.

    Twitter endpoint: /lists/subscribers/create

    Args:
      owner_screen_name:
        The screen_name of the user who owns the list being requested by a slug.
      owner_id:
        The user ID of the user who owns the list being requested by a slug.
      list_id:
        The numerical id of the list.
      slug:
        You can identify a list by its slug instead of its numerical id. If you
        decide to do so, note that you'll also have to specify the list owner
        using the owner_id or owner_screen_name parameters.
    Returns:
      A twitter.User instance representing the user subscribed
    '''
    url = '%s/lists/subscribers/create.json' % (self.base_url)
    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")
    data = {}
    if list_id:
      try:
        data['list_id'] = long(list_id)
      except ValueError:
        raise TwitterError("list_id must be an integer")
    elif slug:
      data['slug'] = slug
      if owner_id:
        try:
          data['owner_id'] = long(owner_id)
        except ValueError:
          raise TwitterError("owner_id must be an integer")
      elif owner_screen_name:
        data['owner_screen_name'] = owner_screen_name
      else:
        raise TwitterError("Identify list by list_id or owner_screen_name/owner_id and slug")
    else:
      raise TwitterError("Identify list by list_id or owner_screen_name/owner_id and slug")
    json = self._RequestUrl(url, 'POST', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    return User.NewFromJsonDict(data)

  def DestroySubscription(self,
                          owner_screen_name=False,
                          owner_id=False,
                          list_id=None,
                          slug=None):
    '''Destroys the subscription to a list for the authenticated user

    The twitter.Api instance must be authenticated.

    Twitter endpoint: /lists/subscribers/destroy

    Args:
      owner_screen_name:
        The screen_name of the user who owns the list being requested by a slug.
      owner_id:
        The user ID of the user who owns the list being requested by a slug.
      list_id:
        The numerical id of the list.
      slug:
        You can identify a list by its slug instead of its numerical id. If you
        decide to do so, note that you'll also have to specify the list owner
        using the owner_id or owner_screen_name parameters.
    Returns:
      A twitter.List instance representing the removed list.
    '''
    url = '%s/lists/subscribers/destroy.json' % (self.base_url)
    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")
    data = {}
    if list_id:
      try:
        data['list_id'] = long(list_id)
      except ValueError:
        raise TwitterError("list_id must be an integer")
    elif slug:
      data['slug'] = slug
      if owner_id:
        try:
          data['owner_id'] = long(owner_id)
        except ValueError:
          raise TwitterError("owner_id must be an integer")
      elif owner_screen_name:
        data['owner_screen_name'] = owner_screen_name
      else:
        raise TwitterError("Identify list by list_id or owner_screen_name/owner_id and slug")
    else:
      raise TwitterError("Identify list by list_id or owner_screen_name/owner_id and slug")
    json = self._RequestUrl(url, 'POST', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    return List.NewFromJsonDict(data)

  def ShowSubscription(self,
                       owner_screen_name=False,
                       owner_id=False,
                       list_id=None,
                       slug=None,
                       user_id=None,
                       screen_name=None,
                       include_entities=False,
                       skip_status=False):
    '''Check if the specified user is a subscriber of the specified list.
    Returns the user if they are subscriber.

    The twitter.Api instance must be authenticated.

    Twitter endpoint: /lists/subscribers/show

    Args:
      owner_screen_name:
        The screen_name of the user who owns the list being requested by a slug.
      owner_id:
        The user ID of the user who owns the list being requested by a slug.
      list_id:
        The numerical id of the list.
      slug:
        You can identify a list by its slug instead of its numerical id. If you
        decide to do so, note that you'll also have to specify the list owner
        using the owner_id or owner_screen_name parameters.
      user_id:
        User_id or a list of User_id's to add to the list. If not given, then screen_name is required.
      screen_name:
        Screen_name or a list of Screen_name's to add to the list. If not given, then user_id is required.
      include_entities:
        If False, the timeline will not contain additional metadata.
        defaults to True. [Optional]
      skip_status:
        If True the statuses will not be returned in the user items.
        [Optional]
    Returns:
      A twitter.User instance representing the user requested
    '''
    url = '%s/lists/subscribers/show.json' % (self.base_url)
    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")
    data = {}
    if list_id:
      try:
        data['list_id'] = long(list_id)
      except ValueError:
        raise TwitterError("list_id must be an integer")
    elif slug:
      data['slug'] = slug
      if owner_id:
        try:
          data['owner_id'] = long(owner_id)
        except ValueError:
          raise TwitterError("owner_id must be an integer")
      elif owner_screen_name:
        data['owner_screen_name'] = owner_screen_name
      else:
        raise TwitterError("Identify list by list_id or owner_screen_name/owner_id and slug")
    else:
      raise TwitterError("Identify list by list_id or owner_screen_name/owner_id and slug")
    if user_id:
      try:
        data['user_id'] = long(user_id)
      except ValueError:
        raise TwitterError("user_id must be an integer")
    elif screen_name:
        data['screen_name'] = screen_name
    if skip_status:
      parameters['skip_status'] = True
    if include_entities:
      parameters['include_entities'] = True
    json = self._RequestUrl(url, 'GET', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    print data
    return User.NewFromJsonDict(data)

  def GetSubscriptions(self, user_id=None, screen_name=None, count=20, cursor=-1):
    '''
    Obtain a collection of the lists the specified user is subscribed to, 20
    lists per page by default. Does not include the user's own lists.

    The twitter.Api instance must be authenticated.

    Twitter endpoint: /lists/subscriptions

    Args:
      user_id:
        The ID of the user for whom to return results for. [Optional]
      screen_name:
        The screen name of the user for whom to return results for.
        [Optional]
      count:
       The amount of results to return per page. Defaults to 20.
       No more than 1000 results will ever be returned in a single page.
      cursor:
        "page" value that Twitter will use to start building the
        list sequence from.  -1 to start at the beginning.
        Twitter will return in the result the values for next_cursor
        and previous_cursor. [Optional]

    Returns:
      A sequence of twitter.List instances, one for each list
    '''
    if not self.__auth:
      raise TwitterError("twitter.Api instance must be authenticated")

    url = '%s/lists/subscriptions.json' % (self.base_url)
    parameters = {}

    try:
      parameters['cursor'] = int(cursor)
    except ValueError:
      raise TwitterError("cursor must be an integer")

    try:
      parameters['count'] = int(count)
    except ValueError:
      raise TwitterError("count must be an integer")

    if user_id is not None:
      try:
        parameters['user_id'] = long(user_id)
      except ValueError:
        raise TwitterError('user_id must be an integer')
    elif screen_name is not None:
      parameters['screen_name'] = screen_name
    else:
      raise TwitterError('Specify user_id or screen_name')

    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    return [List.NewFromJsonDict(x) for x in data['lists']]

  def GetListsList(self,
                   screen_name,
                   user_id=None,
                   reverse=False):
    '''Returns a single status message, specified by the id parameter.

    The twitter.Api instance must be authenticated.

    Twitter endpoint: /lists/list

    Args:
      screen_name:
        Specifies the screen name of the user for whom to return the
        user_timeline. Helpful for disambiguating when a valid screen
        name is also a user ID.
      user_id:
        Specifies the ID of the user for whom to return the
        user_timeline. Helpful for disambiguating when a valid user ID
        is also a valid screen name. [Optional]
      reverse:
        If False, the owned lists will be returned first, othewise subscribed
        lists will be at the top. Returns a maximum of 100 entries regardless.
        Defaults to False. [Optional]
    Returns:
      A list of twitter List items.
    '''
    url = '%s/lists/list.json' % (self.base_url)

    if not self.__auth:
      raise TwitterError("API must be authenticated.")

    parameters = {}

    if user_id:
      parameters['user_id'] = user_id
    elif screen_name:
      parameters['screen_name'] = screen_name

    if reverse:
      parameters['reverse'] = 'true'

    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    return [List.NewFromJsonDict(x) for x in data]

  def GetListTimeline(self,
                      list_id,
                      slug,
                      owner_id=None,
                      owner_screen_name=None,
                      since_id=None,
                      max_id=None,
                      count=None,
                      include_rts=True,
                      include_entities=True):
    '''Fetch the sequence of Status messages for a given list id.

    The twitter.Api instance must be authenticated if the user is private.

    Twitter endpoint: /lists/statuses

    Args:
      list_id:
        Specifies the ID of the list to retrieve.
      slug:
        The slug name for the list to retrieve. If you specify None for the
        list_id, then you have to provide either a owner_screen_name or owner_id.
      owner_id:
        Specifies the ID of the user for whom to return the
        list timeline. Helpful for disambiguating when a valid user ID
        is also a valid screen name. [Optional]
      owner_screen_name:
        Specifies the screen name of the user for whom to return the
        user_timeline. Helpful for disambiguating when a valid screen
        name is also a user ID. [Optional]
      since_id:
        Returns results with an ID greater than (that is, more recent
        than) the specified ID. There are limits to the number of
        Tweets which can be accessed through the API. If the limit of
        Tweets has occurred since the since_id, the since_id will be
        forced to the oldest ID available. [Optional]
      max_id:
        Returns only statuses with an ID less than (that is, older
        than) or equal to the specified ID. [Optional]
      count:
        Specifies the number of statuses to retrieve. May not be
        greater than 200.  [Optional]
      include_rts:
        If True, the timeline will contain native retweets (if they
        exist) in addition to the standard stream of tweets. [Optional]
      include_entities:
        If False, the timeline will not contain additional metadata.
        defaults to True. [Optional]

    Returns:
      A sequence of Status instances, one for each message up to count
    '''
    parameters = { 'slug':    slug,
                   'list_id': list_id,
                 }
    url = '%s/lists/statuses.json' % (self.base_url)

    parameters['slug']    = slug
    parameters['list_id'] = list_id

    if list_id is None:
      if slug is None:
        raise TwitterError('list_id or slug required')
      if owner_id is None and not owner_screen_name:
        raise TwitterError('if list_id is not given you have to include an owner to help identify the proper list')

    if owner_id:
      parameters['owner_id'] = owner_id
    if owner_screen_name:
      parameters['owner_screen_name'] = owner_screen_name

    if since_id:
      try:
        parameters['since_id'] = long(since_id)
      except ValueError:
        raise TwitterError("since_id must be an integer")

    if max_id:
      try:
        parameters['max_id'] = long(max_id)
      except ValueError:
        raise TwitterError("max_id must be an integer")

    if count:
      try:
        parameters['count'] = int(count)
      except ValueError:
        raise TwitterError("count must be an integer")

    if not include_rts:
      parameters['include_rts'] = 'false'

    if not include_entities:
      parameters['include_entities'] = 'false'

    json = self._RequestUrl(url, 'GET', data=parameters)
    data = self._ParseAndCheckTwitter(json.content)
    return [Status.NewFromJsonDict(x) for x in data]

  def GetListMembers(self, list_id, slug, owner_id=None, owner_screen_name=None, cursor=-1, skip_status=False, include_entities=False):
    '''Fetch the sequence of twitter.User instances, one for each member
    of the given list_id or slug.

    The twitter.Api instance must be authenticated.

    Twitter endpoint: /lists/members

    Args:
      list_id:
        Specifies the ID of the list to retrieve.
      slug:
        The slug name for the list to retrieve. If you specify None for the
        list_id, then you have to provide either a owner_screen_name or owner_id.
      owner_id:
        Specifies the ID of the user for whom to return the
        list timeline. Helpful for disambiguating when a valid user ID
        is also a valid screen name. [Optional]
      owner_screen_name:
        Specifies the screen name of the user for whom to return the
        user_timeline. Helpful for disambiguating when a valid screen
        name is also a user ID. [Optional]
      cursor:
        Should be set to -1 for the initial call and then is used to
        control what result page Twitter returns [Optional(ish)]
      skip_status:
        If True the statuses will not be returned in the user items.
        [Optional]
      include_entities:
        If False, the timeline will not contain additional metadata.
        defaults to True. [Optional]

    Returns:
      A sequence of twitter.User instances, one for each follower
    '''
    parameters = { 'slug':    slug,
                   'list_id': list_id,
                 }
    url = '%s/lists/members.json' % (self.base_url)

    parameters['slug']    = slug
    parameters['list_id'] = list_id

    if list_id is None:
      if slug is None:
        raise TwitterError('list_id or slug required')
      if owner_id is None and not owner_screen_name:
        raise TwitterError('if list_id is not given you have to include an owner to help identify the proper list')

    if owner_id:
      parameters['owner_id'] = owner_id
    if owner_screen_name:
      parameters['owner_screen_name'] = owner_screen_name
    if cursor:
      try:
        parameters['cursor'] = int(cursor)
      except ValueError:
        raise TwitterError("cursor must be an integer")
    if skip_status:
      parameters['skip_status'] = True
    if include_entities:
      parameters['include_user_entities'] = True
    result = []
    while True:
      parameters['cursor'] = cursor
      json = self._RequestUrl(url, 'GET', data=parameters)
      data = self._ParseAndCheckTwitter(json.content)
      result += [User.NewFromJsonDict(x) for x in data['users']]
      if 'next_cursor' in data:
        if data['next_cursor'] == 0 or data['next_cursor'] == data['previous_cursor']:
          break
        else:
          cursor = data['next_cursor']
      else:
        break
      sec = self.GetSleepTime('/followers/list')
      time.sleep(sec) 

    return result

  def CreateListsMember(self,
                        list_id=None,
                        slug=None,
                        user_id=None,
                        screen_name=None,
                        owner_screen_name=None,
                        owner_id=None):
    '''Add a new member (or list of members) to a user's list

    The twitter.Api instance must be authenticated.

    Twitter endpoint: /lists/members/create or /lists/members/create_all

    Args:
      list_id:
        The numerical id of the list.
      slug:
        You can identify a list by its slug instead of its numerical id. If you
        decide to do so, note that you'll also have to specify the list owner
        using the owner_id or owner_screen_name parameters.
      user_id:
        User_id or a list of User_id's to add to the list. If not given, then screen_name is required.
      screen_name:
        Screen_name or a list of Screen_name's to add to the list. If not given, then user_id is required.
      owner_screen_name:
        The screen_name of the user who owns the list being requested by a slug.
      owner_id:
        The user ID of the user who owns the list being requested by a slug.
    Returns:
      A twitter.List instance representing the list subscribed to
    '''
    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")
    isList = False
    data = {}
    if list_id:
      try:
        data['list_id'] = long(list_id)
      except ValueError:
        raise TwitterError("list_id must be an integer")
    elif slug:
      data['slug'] = slug
      if owner_id:
        try:
          data['owner_id'] = long(owner_id)
        except ValueError:
          raise TwitterError("owner_id must be an integer")
      elif owner_screen_name:
        data['owner_screen_name'] = owner_screen_name
      else:
        raise TwitterError("Identify list by list_id or owner_screen_name/owner_id and slug")
    else:
      raise TwitterError("Identify list by list_id or owner_screen_name/owner_id and slug")
    if user_id:
      try:
        if type(user_id) == types.ListType or type(user_id) == types.TupleType:
          isList = True
          data['user_id'] = '%s' % ','.join(user_id)
        else:
          data['user_id'] = long(user_id)
      except ValueError:
        raise TwitterError("user_id must be an integer")
    elif screen_name:
        if type(screen_name) == types.ListType or type(screen_name) == types.TupleType:
          isList = True
          data['screen_name'] = '%s' % ','.join(screen_name)
        else:
          data['screen_name'] = screen_name
    if isList:
      url = '%s/lists/members/create_all.json' % self.base_url
    else:
      url = '%s/lists/members/create.json' % self.base_url
    json = self._RequestUrl(url, 'POST', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    return List.NewFromJsonDict(data)

  def DestroyListsMember(self,
                         list_id=None,
                         slug=None,
                         owner_screen_name=False,
                         owner_id=False,
                         user_id=None,
                         screen_name=None):
    '''Destroys the subscription to a list for the authenticated user

    The twitter.Api instance must be authenticated.

    Twitter endpoint: /lists/subscribers/destroy

    Args:
      list_id:
        The numerical id of the list.
      slug:
        You can identify a list by its slug instead of its numerical id. If you
        decide to do so, note that you'll also have to specify the list owner
        using the owner_id or owner_screen_name parameters.
      owner_screen_name:
        The screen_name of the user who owns the list being requested by a slug.
      owner_id:
        The user ID of the user who owns the list being requested by a slug.
      user_id:
        User_id or a list of User_id's to add to the list. If not given, then screen_name is required.
      screen_name:
        Screen_name or a list of Screen_name's to add to the list. If not given, then user_id is required.
    Returns:
      A twitter.List instance representing the removed list.
    '''
    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")
    isList = False
    data = {}
    if list_id:
      try:
        data['list_id'] = long(list_id)
      except ValueError:
        raise TwitterError("list_id must be an integer")
    elif slug:
      data['slug'] = slug
      if owner_id:
        try:
          data['owner_id'] = long(owner_id)
        except ValueError:
          raise TwitterError("owner_id must be an integer")
      elif owner_screen_name:
        data['owner_screen_name'] = owner_screen_name
      else:
        raise TwitterError("Identify list by list_id or owner_screen_name/owner_id and slug")
    else:
      raise TwitterError("Identify list by list_id or owner_screen_name/owner_id and slug")
    if user_id:
      try:
        if type(user_id) == types.ListType or type(user_id) == types.TupleType:
          isList = True
          data['user_id'] = '%s' % ','.join(user_id)
        else:
          data['user_id'] = long(user_id)
      except ValueError:
        raise TwitterError("user_id must be an integer")
    elif screen_name:
        if type(screen_name) == types.ListType or type(screen_name) == types.TupleType:
          isList = True
          data['screen_name'] = '%s' % ','.join(screen_name)
        else:
          data['screen_name'] = screen_name
    if isList:
      url = '%s/lists/members/destroy_all.json' % self.base_url
    else:
      url = '%s/lists/members/destroy.json' % (self.base_url)
    json = self._RequestUrl(url, 'POST', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    return List.NewFromJsonDict(data)

  def GetLists(self, user_id=None, screen_name=None, count=None, cursor=-1):
    '''Fetch the sequence of lists for a user.

    The twitter.Api instance must be authenticated.

    Twitter endpoint: /lists/ownerships

    Args:
      user_id:
        The ID of the user for whom to return results for. [Optional]
      screen_name:
        The screen name of the user for whom to return results for.
        [Optional]
      count:
        The amount of results to return per page. Defaults to 20. No more than
        1000 results will ever be returned in a single page.
        [Optional]
      cursor:
        "page" value that Twitter will use to start building the
        list sequence from.  -1 to start at the beginning.
        Twitter will return in the result the values for next_cursor
        and previous_cursor. [Optional]

    Returns:
      A sequence of twitter.List instances, one for each list
    '''
    if not self.__auth:
      raise TwitterError("twitter.Api instance must be authenticated")

    url = '%s/lists/ownerships.json' % self.base_url
    result = []
    parameters = {}
    if user_id is not None:
      try:
        parameters['user_id'] = long(user_id)
      except ValueError:
        raise TwitterError('user_id must be an integer')
    elif screen_name is not None:
      parameters['screen_name'] = screen_name
    else:
      raise TwitterError('Specify user_id or screen_name')
    if count is not None:
      parameters['count'] = count

    while True:
      parameters['cursor'] = cursor
      json = self._RequestUrl(url, 'GET', data=parameters)
      data = self._ParseAndCheckTwitter(json.content)
      result += [List.NewFromJsonDict(x) for x in data['lists']]
      if 'next_cursor' in data:
        if data['next_cursor'] == 0 or data['next_cursor'] == data['previous_cursor']:
          break
        else:
          cursor = data['next_cursor']
      else:
        break
    return result

  def UpdateProfile(self,
                    name=None,
                    profileURL=None,
                    location=None,
                    description=None,
                    include_entities=False,
                    skip_status=False
                    ):
    '''Update's the authenticated user's profile data.

    The twitter.Api instance must be authenticated.

    Args:
      name:
        Full name associated with the profile. Maximum of 20 characters.
        [Optional]
      profileURL:
        URL associated with the profile. Will be prepended with "http://" if not present. Maximum of 100 characters.
        [Optional]
      location:
        The city or country describing where the user of the account is located. The contents are not normalized or geocoded in any way. Maximum of 30 characters.
        [Optional]
      description:
        A description of the user owning the account. Maximum of 160 characters.
        [Optional]
      include_entities:
        The entities node will not be included when set to false.
        [Optional]
      skip_status:
        When set to either true, t or 1 statuses will not be included in the returned user objects.
        [Optional]
      

    Returns:
      A twitter.User instance representing the modified user.
    '''
    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")

    url = '%s/account/update_profile.json' % (self.base_url)

    data = {}
    if name:
      data['name'] = name
    if profileURL:
      data['url'] = profileURL
    if location:
      data['location'] = location
    if description:
      data['description'] = description
    if include_entities:
      data['include_entities'] = include_entities
    if skip_status:
      data['skip_status'] = skip_status

    json = self._RequestUrl(url, 'POST', data=data)
    data = self._ParseAndCheckTwitter(json.content)
    return User.NewFromJsonDict(data)

  def UpdateBanner(self,
                  image,
                  include_entities=False,
                  skip_status=False):
    '''Updates the authenticated users profile banner

    The twitter.Api instance must be authenticated.

    Args:
      image:
        Location of image in file system
      include_entities:
        If True, each tweet will include a node called "entities,".
        This node offers a variety of metadata about the tweet in a
        discrete structure, including: user_mentions, urls, and hashtags.
        [Optional]
      slug:
        You can identify a list by its slug instead of its numerical id. If you
        decide to do so, note that you'll also have to specify the list owner
        using the owner_id or owner_screen_name parameters.
    Returns:
      A twitter.List instance representing the list subscribed to
    '''
    url = '%s/account/update_profile_banner.json' % (self.base_url)
    if not self.__auth:
      raise TwitterError("The twitter.Api instance must be authenticated.")
    
    with open(image, 'rb') as image_file:
      encoded_image = base64.b64encode(image_file.read())

    data = {
      # When updated for API v1.1 use image, not banner
      # https://dev.twitter.com/docs/api/1.1/post/account/update_profile_banner
      # 'image': encoded_image
      'banner': encoded_image
    }

    if include_entities:
      data['include_entities'] = 1

    if skip_status:
      data['skip_status'] = 1

    json = self._RequestUrl(url, 'POST', data=data)
    if json.status_code in [200, 201, 202]:
      return True

    if json.status_code == 400:
      raise TwitterError("Image data could not be processed")

    if json.status_code == 422:
      raise TwitterError("The image could not be resized or is too large.")

    raise TwitterError("Unkown banner image upload issue")


  def GetStreamSample(self, delimited=None, stall_warnings=None):
    '''
    Returns a small sample of public statuses

    args:
      delimited:      specifies a message length            [optional]
      stall_warnings: set to True to deliver stall warnings [optional]

    returns:
      a twitter stream
    '''
    if not self.__auth:
      raise TwitterError("twitter.Api instance must be authenticated")

    url = '%s/statuses/sample.json' % self.stream_url
    json = self._RequestStream(url, 'GET')
    for line in json.iter_lines():
      if line:
        data = self._ParseAndCheckTwitter(line)
        yield data

  def GetStreamFilter(self, follow=None, track=None, locations=None,
                      delimited=None, stall_warning=None):
    '''Returns a filtered view of public statuses.

    args:
      follow:         a list of user ids to track           [optional]
      track:          a list of expressions to track        [optional]
      locations:      a list of pairs strings 'lat,lon', specifying
                      bounding boxes for the tweets' origin [optional]
      delimited:      specifies a message length            [optional]
      stall_warnings: set to True to deliver stall warnings [optional]

    returns:
      a twitter stream

    '''
    if not self.__auth:
      raise TwitterError("twitter.Api instance must be authenticated")

    if all((follow is None, track is None, locations is None)):
      raise ValueError('No filter parameters specified.')

    data = {}
    if follow is not None:
      data['follow'] = ','.join(follow)
    if track is not None:
      data['track'] = ','.join(track)
    if locations is not None:
      data['locations'] = ','.join(locations)
    if delimited is not None:
      data['delimited'] = str(delimited)
    if delimited is not None:
      data['stall_warning'] = str(stall_warning)

    url = '%s/statuses/filter.json' % self.stream_url
    json = self._RequestStream(url, 'POST', data=data)
    for line in json.iter_lines():
      if line:
        data = self._ParseAndCheckTwitter(line)
        yield data

  def GetUserStream(self, replies='all', withuser='user', track=None, locations=None,
                    delimited=None, stall_warning=None, stringify_friend_ids=False):
    '''Returns the data from the user stream

    args:
      replies:        
        Specifies whether to return additional @replies
        default is 'all'
      withuser: 
        specifies whether to return information for just the authenticating
        user, or include messages from accounts the user follows.
        [optional]
      track:
        a list of expressions to track
        [optional]
      locations:
        a list of pairs strings 'lat,lon', specifying bounding boxes for the
        tweets' origin
        [optional]
      delimited:
        specifies a message length
        [optional]
      stall_warnings:
        set to True to deliver stall warnings
        [optional]
      stringify_friend_ids:
        Specifies whether to send the friends list preamble as an array of
        integers or an array of strings
        [optional]
    returns:
      a twitter stream
    '''
    if not self.__auth:
      raise TwitterError("twitter.Api instance must be authenticated")

    data = {}
    if stringify_friend_ids:
      data['stringify_friend_ids'] = 'true'
    if replies is not None:
      data['replies'] = replies
    if withuser is not None:
      data['with'] = withuser
    if track is not None:
      data['track'] = ','.join(track)
    if locations is not None:
      data['locations'] = ','.join(locations)
    if delimited is not None:
      data['delimited'] = str(delimited)
    if delimited is not None:
      data['stall_warning'] = str(stall_warning)

    url = 'https://userstream.twitter.com/1.1/user.json'
    r = self._RequestStream(url, 'POST', data=data)
    for line in r.iter_lines():
      if len(line) > 0:
        data = simplejson.loads(line)
        yield data

  def VerifyCredentials(self):
    '''Returns a twitter.User instance if the authenticating user is valid.

    Returns:
      A twitter.User instance representing that user if the
      credentials are valid, None otherwise.
    '''
    if not self.__auth:
      raise TwitterError("Api instance must first be given user credentials.")
    url = '%s/account/verify_credentials.json' % self.base_url
    json = self._RequestUrl(url, 'GET')  # No_cache
    data = self._ParseAndCheckTwitter(json.content)
    return User.NewFromJsonDict(data)

  def SetCache(self, cache):
    '''Override the default cache.  Set to None to prevent caching.

    Args:
      cache:
        An instance that supports the same API as the twitter._FileCache
    '''
    if cache == DEFAULT_CACHE:
      self._cache = _FileCache()
    else:
      self._cache = cache

  def SetUrllib(self, urllib):
    '''Override the default urllib implementation.

    Args:
      urllib:
        An instance that supports the same API as the urllib2 module
    '''
    self._urllib = urllib

  def SetCacheTimeout(self, cache_timeout):
    '''Override the default cache timeout.

    Args:
      cache_timeout:
        Time, in seconds, that responses should be reused.
    '''
    self._cache_timeout = cache_timeout

  def SetUserAgent(self, user_agent):
    '''Override the default user agent

    Args:
      user_agent:
        A string that should be send to the server as the User-agent
    '''
    self._request_headers['User-Agent'] = user_agent

  def SetXTwitterHeaders(self, client, url, version):
    '''Set the X-Twitter HTTP headers that will be sent to the server.

    Args:
      client:
         The client name as a string.  Will be sent to the server as
         the 'X-Twitter-Client' header.
      url:
         The URL of the meta.xml as a string.  Will be sent to the server
         as the 'X-Twitter-Client-URL' header.
      version:
         The client version as a string.  Will be sent to the server
         as the 'X-Twitter-Client-Version' header.
    '''
    self._request_headers['X-Twitter-Client'] = client
    self._request_headers['X-Twitter-Client-URL'] = url
    self._request_headers['X-Twitter-Client-Version'] = version

  def SetSource(self, source):
    '''Suggest the "from source" value to be displayed on the Twitter web site.

    The value of the 'source' parameter must be first recognized by
    the Twitter server.  New source values are authorized on a case by
    case basis by the Twitter development team.

    Args:
      source:
        The source name as a string.  Will be sent to the server as
        the 'source' parameter.
    '''
    self._default_params['source'] = source

  def GetRateLimitStatus(self, resource_families=None):
    '''Fetch the rate limit status for the currently authorized user.

    Args:
      resources:
        A comma seperated list of resource families you want to know the current
        rate limit disposition of.
        [Optional]

    Returns:
      A dictionary containing the time the limit will reset (reset_time),
      the number of remaining hits allowed before the reset (remaining_hits),
      the number of hits allowed in a 60-minute period (hourly_limit), and
      the time of the reset in seconds since The Epoch (reset_time_in_seconds).
    '''
    parameters = {}
    if resource_families is not None:
      parameters['resources'] = resource_families

    url = '%s/application/rate_limit_status.json' % self.base_url
    json = self._RequestUrl(url, 'GET', data=parameters)  # No-Cache
    data = self._ParseAndCheckTwitter(json.content)
    return data

  def GetAverageSleepTime(self, resources):
    '''Determines the minimum number of seconds that a program must wait
    before hitting the server again without exceeding the rate_limit
    imposed for the currently authenticated user.

    Returns:
      The average seconds that the api must have to sleep       
    '''
    if resources[0] == '/':
        resources = resources[1:]
    
    resource_families = resources[:resources.find('/')] if '/' in resources else resources
    
    rate_status = self.GetRateLimitStatus(resource_families)
    try:
        reset_time = rate_status['resources'][resource_families]['/' + resources]['reset']
        remaining = rate_status['resources'][resource_families]['/' + resources]['remaining']
    except:
        raise TwitterError('Wrong resources')
    
    utc_now = datetime.datetime.utcnow()
    utc_stuct = utc_now.timetuple()
    current_time = timegm(utc_stuct)
    delta = reset_time - current_time
    
    if remaining == 0:
        return remaining
    else:
        return delta/ remaining

  def GetSleepTime(self, resources):
    '''Determines the minimum number of seconds that a program must wait
    before hitting the server again without exceeding the rate_limit
    imposed for the currently authenticated user.

    Returns:
      The minimum seconds that the api must have to sleep before query again      
    '''
    if resources[0] == '/':
        resources = resources[1:]
    
    resource_families = resources[:resources.find('/')] if '/' in resources else resources
    
    rate_status = self.GetRateLimitStatus(resource_families)
    try:
        reset_time = rate_status['resources'][resource_families]['/' + resources]['reset']
        remaining = rate_status['resources'][resource_families]['/' + resources]['remaining']
    except:
        raise TwitterError('Wrong resources')

    if remaining == 0:
        utc_now = datetime.datetime.utcnow()
        utc_stuct = utc_now.timetuple()
        current_time = timegm(utc_stuct)
        delta = reset_time - current_time
        return delta
    else:
        return 0

  def _BuildUrl(self, url, path_elements=None, extra_params=None):
    # Break url into constituent parts
    (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)

    # Add any additional path elements to the path
    if path_elements:
      # Filter out the path elements that have a value of None
      p = [i for i in path_elements if i]
      if not path.endswith('/'):
        path += '/'
      path += '/'.join(p)

    # Add any additional query parameters to the query string
    if extra_params and len(extra_params) > 0:
      extra_query = self._EncodeParameters(extra_params)
      # Add it to the existing query
      if query:
        query += '&' + extra_query
      else:
        query = extra_query

    # Return the rebuilt URL
    return urlparse.urlunparse((scheme, netloc, path, params, query, fragment))

  def _InitializeRequestHeaders(self, request_headers):
    if request_headers:
      self._request_headers = request_headers
    else:
      self._request_headers = {}

  def _InitializeUserAgent(self):
    user_agent = 'Python-urllib/%s (python-twitter/%s)' % \
                 (self._urllib.__version__, __version__)
    self.SetUserAgent(user_agent)

  def _InitializeDefaultParameters(self):
    self._default_params = {}

  def _DecompressGzippedResponse(self, response):
    raw_data = response.read()
    if response.headers.get('content-encoding', None) == 'gzip':
      url_data = gzip.GzipFile(fileobj=StringIO.StringIO(raw_data)).read()
    else:
      url_data = raw_data
    return url_data

  def _Encode(self, s):
    if self._input_encoding:
      return unicode(s, self._input_encoding).encode('utf-8')
    else:
      return unicode(s).encode('utf-8')

  def _EncodeParameters(self, parameters):
    '''Return a string in key=value&key=value form

    Values of None are not included in the output string.

    Args:
      parameters:
        A dict of (key, value) tuples, where value is encoded as
        specified by self._encoding

    Returns:
      A URL-encoded string in "key=value&key=value" form
    '''
    if parameters is None:
      return None
    else:
      return urllib.urlencode(dict([(k, self._Encode(v)) for k, v in parameters.items() if v is not None]))

  def _EncodePostData(self, post_data):
    '''Return a string in key=value&key=value form

    Values are assumed to be encoded in the format specified by self._encoding,
    and are subsequently URL encoded.

    Args:
      post_data:
        A dict of (key, value) tuples, where value is encoded as
        specified by self._encoding

    Returns:
      A URL-encoded string in "key=value&key=value" form
    '''
    if post_data is None:
      return None
    else:
      return urllib.urlencode(dict([(k, self._Encode(v)) for k, v in post_data.items()]))

  def _ParseAndCheckTwitter(self, json):
    """Try and parse the JSON returned from Twitter and return
    an empty dictionary if there is any error. This is a purely
    defensive check because during some Twitter network outages
    it will return an HTML failwhale page."""
    try:
      data = simplejson.loads(json)
      self._CheckForTwitterError(data)
    except ValueError:
      if "<title>Twitter / Over capacity</title>" in json:
        raise TwitterError("Capacity Error")
      if "<title>Twitter / Error</title>" in json:
        raise TwitterError("Technical Error")
      raise TwitterError("json decoding")

    return data

  def _CheckForTwitterError(self, data):
    """Raises a TwitterError if twitter returns an error message.

    Args:
      data:
        A python dict created from the Twitter json response

    Raises:
      TwitterError wrapping the twitter error message if one exists.
    """
    # Twitter errors are relatively unlikely, so it is faster
    # to check first, rather than try and catch the exception
    if 'error' in data:
      raise TwitterError(data['error'])
    if 'errors' in data:
      raise TwitterError(data['errors'])

  def _RequestUrl(self, url, verb, data=None):
    '''Reqeust a Url

       Args:
         url:   the web location we want to retrieve
         verb:  POST, GET, etc...
         data:  A dict of (str, unicode) key/value pairs.

       Returns:
         A JSON object.
    '''
    if verb == 'POST':
      if data.has_key('media'):
        return requests.post(
          url,
          files=data,
          auth=self.__auth,
          timeout=self._requests_timeout
        )
      else:
        return requests.post(
          url,
          data=data,
          auth=self.__auth,
          timeout=self._requests_timeout
        )
    if verb == 'GET':
      url = self._BuildUrl(url, extra_params=data)
      return requests.get(
        url,
        auth=self.__auth,
        timeout=self._requests_timeout
      )
    return 0  # if not a POST or GET request

  def _RequestStream(self, url, verb, data=None):
    '''Reqeust a stream of data

       Args:
         url:   the web location we want to retrieve
         verb:  POST, GET, etc...
         data:  A dict of (str, unicode) key/value pairs.

       Returns:
         A twitter stream.
    '''

    if verb == 'POST':
      return requests.post(url, data=data, stream=True,
                           auth=self.__auth)
    
    if verb == 'POST':  return requests.post(url, data=data, stream=True,
                                             auth=self.__auth,
                                             timeout=self._requests_timeout
                                             )

    if verb == 'GET':
      url = self._BuildUrl(url, extra_params=data)
      return requests.get(url, stream=True, auth=self.__auth,
                          timeout=self._requests_timeout
                          )
    return 0  # if not a POST or GET request
