#!/usr/bin/env python

from calendar import timegm
import rfc822
import time
from sets import Set

from twitter import json, Hashtag, Url
from twitter.media import Media


class Status(object):
    """A class representing the Status structure used by the twitter API.

    The Status structure exposes the following properties:

      status.contributors
      status.coordinates
      status.created_at
      status.created_at_in_seconds # read only
      status.favorited
      status.favorite_count
      status.geo
      status.id
      status.id_str
      status.in_reply_to_screen_name
      status.in_reply_to_user_id
      status.in_reply_to_status_id
      status.lang
      status.place
      status.retweet_count
      status.relative_created_at # read only
      status.source
      status.text
      status.truncated
      status.location
      status.user
      status.urls
      status.user_mentions
      status.hashtags
    """

    def __init__(self, **kwargs):
        """An object to hold a Twitter status message.

        This class is normally instantiated by the twitter.Api class and
        returned in a sequence.

        Note: Dates are posted in the form "Sat Jan 27 04:17:38 +0000 2007"

        Args:
          created_at:
            The time this status message was posted. [Optional]
          favorited:
            Whether this is a favorite of the authenticated user. [Optional]
          favorite_count:
            Number of times this status message has been favorited. [Optional]
          id:
            The unique id of this status message. [Optional]
          id_str:
            The string form of the unique id of this status message. [Optional]
          text:
            The text of this status message. [Optional]
          location:
            the geolocation string associated with this message. [Optional]
          relative_created_at:
            A human readable string representing the posting time. [Optional]
          user:
            A twitter.User instance representing the person posting the
            message. [Optional]
          now:
            The current time, if the client chooses to set it.
            Defaults to the wall clock time. [Optional]
          urls:
          user_mentions:
          hashtags:
          geo:
          place:
          coordinates:
          contributors:
          retweeted:
          retweeted_status:
          current_user_retweet:
          retweet_count:
          possibly_sensitive:
          scopes:
          withheld_copyright:
          withheld_in_countries:
          withheld_scope:
        """
        param_defaults = {
            'coordinates': None,
            'contributors': None,
            'created_at': None,
            'current_user_retweet': None,
            'favorited': None,
            'favorite_count': None,
            'geo': None,
            'id': None,
            'id_str': None,
            'in_reply_to_screen_name': None,
            'in_reply_to_user_id': None,
            'in_reply_to_status_id': None,
            'lang': None,
            'location': None,
            'now': None,
            'place': None,
            'possibly_sensitive': None,
            'retweeted': None,
            'retweeted_status': None,
            'retweet_count': None,
            'scopes': None,
            'source': None,
            'text': None,
            'truncated': None,
            'urls': None,
            'user': None,
            'user_mentions': None,
            'hashtags': None,
            'media': None,
            'withheld_copyright': None,
            'withheld_in_countries': None,
            'withheld_scope': None,
        }

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    # Properties that you should be able to set yourself.

    @property
    def Text(self):
        """Get the text of this status message.

        Returns:
          The text of this status message.
        """
        return self._text

    @Text.setter
    def Text(self, text):
        self._text = text

    @property
    def InReplyToStatusId(self):
        return self._in_reply_to_status_id

    @InReplyToStatusId.setter
    def InReplyToStatusId(self, in_reply_to_status_id):
        self._in_reply_to_status_id = in_reply_to_status_id

    @property
    def Possibly_sensitive(self):
        return self._possibly_sensitive

    @Possibly_sensitive.setter
    def Possibly_sensitive(self, possibly_sensitive):
        self._possibly_sensitive = possibly_sensitive

    @property
    def Place(self):
        return self._place

    @Place.setter
    def Place(self, place):
        self._place = place

    @property
    def Coordinates(self):
        return self._coordinates

    @Coordinates.setter
    def Coordinates(self, coordinates):
        self._coordinates = coordinates

    # Missing the following, media_ids, trim_user, display_coordinates,
    # lat and long

    @property
    def CreatedAt(self):
        """Get the time this status message was posted.

        Returns:
          The time this status message was posted
        """
        return self._created_at

    @property
    def CreatedAtInSeconds(self):
        """Get the time this status message was posted, in seconds since the epoch.

        Returns:
          The time this status message was posted, in seconds since the epoch.
        """
        return timegm(rfc822.parsedate(self.created_at))

    @property
    def RelativeCreatedAt(self):
        """Get a human readable string representing the posting time

        Returns:
          A human readable string representing the posting time
        """
        fudge = 1.25
        delta = long(self.now) - long(self.CreatedAtInSeconds)

        if delta < (1 * fudge):
            return 'about a second ago'
        elif delta < (60 * (1 / fudge)):
            return 'about %d seconds ago' % (delta)
        elif delta < (60 * fudge):
            return 'about a minute ago'
        elif delta < (60 * 60 * (1 / fudge)):
            return 'about %d minutes ago' % (delta / 60)
        elif delta < (60 * 60 * fudge) or delta / (60 * 60) == 1:
            return 'about an hour ago'
        elif delta < (60 * 60 * 24 * (1 / fudge)):
            return 'about %d hours ago' % (delta / (60 * 60))
        elif delta < (60 * 60 * 24 * fudge) or delta / (60 * 60 * 24) == 1:
            return 'about a day ago'
        else:
            return 'about %d days ago' % (delta / (60 * 60 * 24))

    @property
    def Favorited(self):
        """Get the favorited setting of this status message.

        Returns:
          True if this status message is favorited; False otherwise
        """
        return self._favorited

    @property
    def FavoriteCount(self):
        """Get the favorite count of this status message.

        Returns:
          number of times this status message has been favorited
        """
        return self._favorite_count

    @property
    def Id(self):
        """Get the unique id of this status message.

        Returns:
          The unique id of this status message
        """
        return self._id

    @property
    def IdStr(self):
        """Get the unique id_str of this status message.

        Returns:
          The unique id_str of this status message
        """
        return self._id_str

    @property
    def InReplyToScreenName(self):
        return self._in_reply_to_screen_name

    @property
    def InReplyToUserId(self):
        return self._in_reply_to_user_id

    @property
    def Truncated(self):
        return self._truncated

    @property
    def Retweeted(self):
        return self._retweeted

    @property
    def Source(self):
        return self._source

    @property
    def Lang(self):
        """Get the machine-detected language of this status message

        Returns:
          The machine-detected language  code of this status message.
        """
        return self._lang

    @property
    def Location(self):
        """Get the geolocation associated with this status message

        Returns:
          The geolocation string of this status message.
        """
        return self._location

    @property
    def User(self):
        """Get a twitter.User representing the entity posting this status message.

        Returns:
          A twitter.User representing the entity posting this status message
        """
        return self._user

    @property
    def Now(self):
        """Get the wallclock time for this status message.

        Used to calculate relative_created_at.  Defaults to the time
        the object was instantiated.

        Returns:
          Whatever the status instance believes the current time to be,
          in seconds since the epoch.
        """
        if self._now is None:
            self._now = time.time()
        return self._now

    @Now.setter
    def Now(self, now):
        self._now = now

    @property
    def Geo(self):
        return self._geo

    @property
    def Contributors(self):
        return self._contributors

    @property
    def Retweeted_status(self):
        return self._retweeted_status

    @property
    def RetweetCount(self):
        return self._retweet_count

    @property
    def Current_user_retweet(self):
        return self._current_user_retweet

    @property
    def Scopes(self):
        return self._scopes

    @property
    def Withheld_copyright(self):
        return self._withheld_copyright

    @property
    def Withheld_in_countries(self):
        return self._withheld_in_countries

    @property
    def Withheld_scope(self):
        return self._withheld_scope

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        try:
            return other and \
                   self.created_at == other.created_at and \
                   self.id == other.id and \
                   self.text == other.text and \
                   self.location == other.location and \
                   self.user == other.user and \
                   self.in_reply_to_screen_name == other.in_reply_to_screen_name and \
                   self.in_reply_to_user_id == other.in_reply_to_user_id and \
                   self.in_reply_to_status_id == other.in_reply_to_status_id and \
                   self.truncated == other.truncated and \
                   self.retweeted == other.retweeted and \
                   self.favorited == other.favorited and \
                   self.favorite_count == other.favorite_count and \
                   self.source == other.source and \
                   self.geo == other.geo and \
                   self.place == other.place and \
                   self.coordinates == other.coordinates and \
                   self.contributors == other.contributors and \
                   self.retweeted_status == other.retweeted_status and \
                   self.retweet_count == other.retweet_count and \
                   self.current_user_retweet == other.current_user_retweet and \
                   self.possibly_sensitive == other.possibly_sensitive and \
                   self.scopes == other.scopes and \
                   self.withheld_copyright == other.withheld_copyright and \
                   self.withheld_in_countries == other.withheld_in_countries and \
                   self.withheld_scope == other.withheld_scope
        except AttributeError:
            return False

    def __str__(self):
        """A string representation of this twitter.Status instance.
        The return value is the same as the JSON string representation.

        Returns:
          A string representation of this twitter.Status instance.
        """
        return self.AsJsonString()

    def __repr__(self):
        """A string representation of this twitter.Status instance.
      The return value is the ID of status, username and datetime.
      Returns:
        A string representation of this twitter.Status instance with
        the ID of status, username and datetime.
      """
        if self.user:
            representation = "Status(ID=%s, screen_name='%s', created_at='%s')" % \
                             (self.id, self.user.screen_name, self.created_at)
        else:
            representation = "Status(ID=%s,  created_at='%s')" % (self.id, self.created_at)
        return representation

    def AsJsonString(self, allow_non_ascii=False):
        """A JSON string representation of this twitter.Status instance.
        To output non-ascii, set keyword allow_non_ascii=True.

        Returns:
          A JSON string representation of this twitter.Status instance
       """
        return json.dumps(self.AsDict(), sort_keys=True, ensure_ascii=not allow_non_ascii)

    def AsDict(self):
        """A dict representation of this twitter.Status instance.
        The return value uses the same key names as the JSON representation.

        Return:
          A dict representing this twitter.Status instance
        """
        data = {}
        if self.created_at:
            data['created_at'] = self.created_at
        if self.favorited:
            data['favorited'] = self.favorited
        if self.favorite_count:
            data['favorite_count'] = self.favorite_count
        if self.id:
            data['id'] = self.id
        if self.text:
            data['text'] = self.text
        if self.lang:
            data['lang'] = self.lang
        if self.location:
            data['location'] = self.location
        if self.user:
            data['user'] = self.user.AsDict()
        if self.in_reply_to_screen_name:
            data['in_reply_to_screen_name'] = self.in_reply_to_screen_name
        if self.in_reply_to_user_id:
            data['in_reply_to_user_id'] = self.in_reply_to_user_id
        if self.in_reply_to_status_id:
            data['in_reply_to_status_id'] = self.in_reply_to_status_id
        if self.truncated is not None:
            data['truncated'] = self.truncated
        if self.retweeted is not None:
            data['retweeted'] = self.retweeted
        if self.favorited is not None:
            data['favorited'] = self.favorited
        if self.source:
            data['source'] = self.source
        if self.geo:
            data['geo'] = self.geo
        if self.place:
            data['place'] = self.place
        if self.coordinates:
            data['coordinates'] = self.coordinates
        if self.contributors:
            data['contributors'] = self.contributors
        if self.hashtags:
            data['hashtags'] = [h.text for h in self.hashtags]
        if self.media:
            data['media'] = [m for m in self.media]
        if self.retweeted_status:
            data['retweeted_status'] = self.retweeted_status.AsDict()
        if self.retweet_count:
            data['retweet_count'] = self.retweet_count
        if self.urls:
            data['urls'] = dict([(url.url, url.expanded_url) for url in self.urls])
        if self.user_mentions:
            data['user_mentions'] = [um.AsDict() for um in self.user_mentions]
        if self.current_user_retweet:
            data['current_user_retweet'] = self.current_user_retweet
        if self.possibly_sensitive:
            data['possibly_sensitive'] = self.possibly_sensitive
        if self.scopes:
            data['scopes'] = self.scopes
        if self.withheld_copyright:
            data['withheld_copyright'] = self.withheld_copyright
        if self.withheld_in_countries:
            data['withheld_in_countries'] = self.withheld_in_countries
        if self.withheld_scope:
            data['withheld_scope'] = self.withheld_scope
        return data

    @staticmethod
    def NewFromJsonDict(data):
        """Create a new instance based on a JSON dict.

        Args:
          data: A JSON dict, as converted from the JSON in the twitter API
        Returns:
          A twitter.Status instance
        """
        if 'user' in data:
            from twitter import User
            # Have to do the import here to prevent cyclic imports in the __init__.py
            # file
            user = User.NewFromJsonDict(data['user'])
        else:
            user = None
        if 'retweeted_status' in data:
            retweeted_status = Status.NewFromJsonDict(data['retweeted_status'])
        else:
            retweeted_status = None

        if 'current_user_retweet' in data:
            current_user_retweet = data['current_user_retweet']['id']
        else:
            current_user_retweet = None

        urls = None
        user_mentions = None
        hashtags = None
        media = Set()
        if 'entities' in data:
            if 'urls' in data['entities']:
                urls = [Url.NewFromJsonDict(u) for u in data['entities']['urls']]
            if 'user_mentions' in data['entities']:
                from twitter import User

                user_mentions = [User.NewFromJsonDict(u) for u in data['entities']['user_mentions']]
            if 'hashtags' in data['entities']:
                hashtags = [Hashtag.NewFromJsonDict(h) for h in data['entities']['hashtags']]
            if 'media' in data['entities']:
                for m in data['entities']['media']:
                    media.add(Media.NewFromJsonDict(m))

        # the new extended entities
        if 'extended_entities' in data:
            if 'media' in data['extended_entities']:
                for m in data['extended_entities']['media']:
                    media.add(Media.NewFromJsonDict(m))

        return Status(created_at=data.get('created_at', None),
                      favorited=data.get('favorited', None),
                      favorite_count=data.get('favorite_count', None),
                      id=data.get('id', None),
                      text=data.get('text', None),
                      location=data.get('location', None),
                      lang=data.get('lang', None),
                      in_reply_to_screen_name=data.get('in_reply_to_screen_name', None),
                      in_reply_to_user_id=data.get('in_reply_to_user_id', None),
                      in_reply_to_status_id=data.get('in_reply_to_status_id', None),
                      truncated=data.get('truncated', None),
                      retweeted=data.get('retweeted', None),
                      source=data.get('source', None),
                      user=user,
                      urls=urls,
                      user_mentions=user_mentions,
                      hashtags=hashtags,
                      media=media,
                      geo=data.get('geo', None),
                      place=data.get('place', None),
                      coordinates=data.get('coordinates', None),
                      contributors=data.get('contributors', None),
                      retweeted_status=retweeted_status,
                      current_user_retweet=current_user_retweet,
                      retweet_count=data.get('retweet_count', None),
                      possibly_sensitive=data.get('possibly_sensitive', None),
                      scopes=data.get('scopes', None),
                      withheld_copyright=data.get('withheld_copyright', None),
                      withheld_in_countries=data.get('withheld_in_countries', None),
                      withheld_scope=data.get('withheld_scope', None),
                      )
