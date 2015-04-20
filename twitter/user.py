#!/usr/bin/env python

from twitter import json, TwitterError  # TwitterError not used


class UserStatus(object):
    """A class representing the UserStatus structure used by the twitter API.

    The UserStatus structure exposes the following properties:

      userstatus.name
      userstatus.id_str
      userstatus.id
      userstatus.screen_name
      userstatus.following
      userstatus.followed_by
    """

    def __init__(self, **kwargs):
        """An object to hold a Twitter user status message.

        This class is normally instantiated by the twitter.Api class and
        returned in a sequence.

        Args:
          id:
            The unique id of this status message. [Optional]
          id_str:
            The string version of the unique id of this status message. [Optional]
        """
        param_defaults = {
            'name': None,
            'id': None,
            'id_str': None,
            'screen_name': None,
            'following': None,
            'followed_by': None}

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    @property
    def FollowedBy(self):
        return self.followed_by or False

    @property
    def Following(self):
        return self.following or False

    @property
    def ScreenName(self):
        return self.screen_name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        try:
            return other and \
                   self.name == other.name and \
                   self.id == other.id and \
                   self.id_str == other.id_str and \
                   self.screen_name == other.screen_name and \
                   self.following == other.following and \
                   self.followed_by == other.followed_by
        except AttributeError:
            return False

    def __str__(self):
        """A string representation of this twitter.UserStatus instance.

        The return value is the same as the JSON string representation.

        Returns:
          A string representation of this twitter.UserStatus instance.
        """
        return self.AsJsonString()

    def AsJsonString(self):
        """A JSON string representation of this twitter.UserStatus instance.

        Returns:
          A JSON string representation of this twitter.UserStatus instance
       """
        return json.dumps(self.AsDict(), sort_keys=True)

    def AsDict(self):
        """A dict representation of this twitter.UserStatus instance.

        The return value uses the same key names as the JSON representation.

        Return:
          A dict representing this twitter.UserStatus instance
        """
        data = {}
        if self.name:
            data['name'] = self.name
        if self.id:
            data['id'] = self.id
        if self.id_str:
            data['id_str'] = self.id_str
        if self.screen_name:
            data['screen_name'] = self.screen_name
        if self.following:
            data['following'] = self.following
        if self.followed_by:
            data['followed_by'] = self.followed_by
        return data

    @staticmethod
    def NewFromJsonDict(data):
        """Create a new instance based on a JSON dict.

        Args:
          data: A JSON dict, as converted from the JSON in the twitter API
        Returns:
          A twitter.UserStatus instance
        """
        following = None
        followed_by = None
        if 'connections' in data:
            if 'following' in data['connections']:
                following = True
            if 'followed_by' in data['connections']:
                followed_by = True

        return UserStatus(name=data.get('name', None),
                          id=data.get('id', None),
                          id_str=data.get('id_str', None),
                          screen_name=data.get('screen_name', None),
                          following=following,
                          followed_by=followed_by)


class User(object):
    """A class representing the User structure used by the twitter API.

    The User structure exposes the following properties:

      user.id
      user.name
      user.screen_name
      user.location
      user.description
      user.default_profile
      user.default_profile_image
      user.profile_image_url
      user.profile_background_tile
      user.profile_background_image_url
      user.profile_banner_url
      user.profile_sidebar_fill_color
      user.profile_background_color
      user.profile_link_color
      user.profile_text_color
      user.protected
      user.utc_offset
      user.time_zone
      user.url
      user.status
      user.statuses_count
      user.followers_count
      user.friends_count
      user.favourites_count
      user.geo_enabled
      user.verified
      user.lang
      user.notifications
      user.contributors_enabled
      user.created_at
      user.listed_count
    """

    def __init__(self, **kwargs):
        param_defaults = {
            'id': None,
            'name': None,
            'screen_name': None,
            'location': None,
            'description': None,
            'default_profile': None,
            'default_profile_image': None,
            'profile_image_url': None,
            'profile_background_tile': None,
            'profile_background_image_url': None,
            'profile_banner_url': None,
            'profile_sidebar_fill_color': None,
            'profile_background_color': None,
            'profile_link_color': None,
            'profile_text_color': None,
            'protected': None,
            'utc_offset': None,
            'time_zone': None,
            'followers_count': None,
            'friends_count': None,
            'statuses_count': None,
            'favourites_count': None,
            'url': None,
            'status': None,
            'geo_enabled': None,
            'verified': None,
            'lang': None,
            'notifications': None,
            'contributors_enabled': None,
            'created_at': None,
            'listed_count': None}

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    @property
    def Id(self):
        """Get the unique id of this user.

        Returns:
          The unique id of this user
        """
        return self._id

    @property.setter
    def Id(self, id):
        self._id = id

    @property
    def Name(self):
        """Get the real name of this user.

        Returns:
          The real name of this user
        """
        return self._name

    @property.setter
    def Name(self, name):
        self._name = name


    @property
    def ScreenName(self):
        """Get the short twitter name of this user.

        Returns:
          The short twitter name of this user
        """
        return self._screen_name

    @property.setter
    def ScreenName(self, screen_name):
        self._screen_name = screen_name

    @property
    def Location(self):
        """Get the geographic location of this user.

        Returns:
          The geographic location of this user
        """
        return self._location

    @property.setter
    def Location(self, location):
        self._location = location

    @property
    def Description(self):
        """Get the short text description of this user.

        Returns:
          The short text description of this user
        """
        return self._description

    @property.setter
    def Description(self, description):
        """Set the short text description of this user.

        Args:
          description: The short text description of this user
        """
        self._description = description

    @property
    def Url(self):
        """Get the homepage url of this user.

        Returns:
          The homepage url of this user
        """
        return self._url

    @property.setter
    def Url(self, url):
        self._url = url

    @property
    def ProfileImageUrl(self):
        """Get the url of the thumbnail of this user.

        Returns:
          The url of the thumbnail of this user
        """
        return self._profile_image_url

    @property.setter
    def ProfileImageUrl(self, profile_image_url):
        self._profile_image_url = profile_image_url

    @property
    def ProfileBackgroundTile(self):
        """Boolean for whether to tile the profile background image.

        Returns:
          True if the background is to be tiled, False if not, None if unset.
        """
        return self._profile_background_tile

    @property.setter
    def ProfileBackgroundTile(self, profile_background_tile):
        self._profile_background_tile = profile_background_tile

    @property
    def ProfileBackgroundImageUrl(self):
        return self._profile_background_image_url

    @property.setter
    def ProfileBackgroundImageUrl(self, profile_background_image_url):
        self._profile_background_image_url = profile_background_image_url

    @property
    def ProfileBannerUrl(self):
        return self._profile_banner_url

    @property.setter
    def ProfileBannerUrl(self, profile_banner_url):
        self._profile_banner_url = profile_banner_url

    @property
    def ProfileSidebarFillColor(self):
        return self._profile_sidebar_fill_color

    @property.setter
    def ProfileSidebarFillColor(self, profile_sidebar_fill_color):
        self._profile_sidebar_fill_color = profile_sidebar_fill_color

    @property
    def GetProfileBackgroundColor(self):
        return self._profile_background_color

    @property.setter
    def ProfileBackgroundColor(self, profile_background_color):
        self._profile_background_color = profile_background_color

    @property
    def ProfileLinkColor(self):
        return self._profile_link_color

    @property.setter
    def ProfileLinkColor(self, profile_link_color):
        self._profile_link_color = profile_link_color

    @property
    def ProfileTextColor(self):
        return self._profile_text_color

    @property.setter
    def ProfileTextColor(self, profile_text_color):
        self._profile_text_color = profile_text_color

    @property
    def Protected(self):
        return self._protected

    @property.setter
    def Protected(self, protected):
        self._protected = protected

    @property
    def UtcOffset(self):
        return self._utc_offset

    @property.setter
    def UtcOffset(self, utc_offset):
        self._utc_offset = utc_offset

    @property
    def TimeZone(self):
        """Returns the current time zone string for the user.

        Returns:
          The descriptive time zone string for the user.
        """
        return self._time_zone

    @property.setter
    def TimeZone(self, time_zone):
        self._time_zone = time_zone

    @property
    def Status(self):
        """Get the latest twitter.Status of this user.

        Returns:
          The latest twitter.Status of this user
        """
        return self._status

    @property.setter
    def Status(self, status):
        self._status = status

    @property
    def FriendsCount(self):
        """Get the friend count for this user.

        Returns:
          The number of users this user has befriended.
        """
        return self._friends_count

    @property.setter
    def FriendsCount(self, count):
        self._friends_count = count

    @property
    def ListedCount(self):
        """Get the listed count for this user.

        Returns:
          The number of lists this user belongs to.
        """
        return self._listed_count

    @property.setter
    def ListedCount(self, count):
        self._listed_count = count

    @property
    def FollowersCount(self):
        """Get the follower count for this user.

        Returns:
          The number of users following this user.
        """
        return self._followers_count

    @property.setter
    def FollowersCount(self, count):
        self._followers_count = count

    @property
    def StatusesCount(self):
        """Get the number of status updates for this user.

        Returns:
          The number of status updates for this user.
        """
        return self._statuses_count

    @property.setter
    def SetStatusesCount(self, count):
        self._statuses_count = count

    @property
    def FavouritesCount(self):
        """Get the number of favourites for this user.

        Returns:
          The number of favourites for this user.
        """
        return self._favourites_count

    @property.setter
    def FavouritesCount(self, count):
        self._favourites_count = count

    @property
    def GeoEnabled(self):
        """Get the setting of geo_enabled for this user.

        Returns:
          True/False if Geo tagging is enabled
        """
        return self._geo_enabled

    @property.setter
    def SetGeoEnabled(self, geo_enabled):
        self._geo_enabled = geo_enabled

    @property
    def Verified(self):
        """Get the setting of verified for this user.

        Returns:
          True/False if user is a verified account
        """
        return self._verified

    @property.setter
    def Verified(self, verified):
        self._verified = verified

    @property
    def Lang(self):
        """Get the setting of lang for this user.

        Returns:
          language code of the user
        """
        return self._lang

    @property.setter
    def Lang(self, lang):
        self._lang = lang

    @property
    def Notifications(self):
        """Get the setting of notifications for this user.

        Returns:
          True/False for the notifications setting of the user
        """
        return self._notifications

    @property.setter
    def Notifications(self, notifications):
        self._notifications = notifications

    @property
    def ContributorsEnabled(self):
        """Get the setting of contributors_enabled for this user.

        Returns:
          True/False contributors_enabled of the user
        """
        return self._contributors_enabled

    @property.setter
    def ContributorsEnabled(self, contributors_enabled):
        self._contributors_enabled = contributors_enabled

    @property
    def CreatedAt(self):
        """Get the setting of created_at for this user.

        Returns:
          created_at value of the user
        """
        return self._created_at

    @property.setter
    def CreatedAt(self, created_at):
        self._created_at = created_at

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        try:
            return other and \
                   self.id == other.id and \
                   self.name == other.name and \
                   self.screen_name == other.screen_name and \
                   self.location == other.location and \
                   self.description == other.description and \
                   self.default_profile == other.default_profile and \
                   self.default_profile_image == other.default_profile_image and \
                   self.profile_image_url == other.profile_image_url and \
                   self.profile_background_tile == other.profile_background_tile and \
                   self.profile_background_image_url == other.profile_background_image_url and \
                   self.profile_banner_url == other.profile_banner_url and \
                   self.profile_sidebar_fill_color == other.profile_sidebar_fill_color and \
                   self.profile_background_color == other.profile_background_color and \
                   self.profile_link_color == other.profile_link_color and \
                   self.profile_text_color == other.profile_text_color and \
                   self.protected == other.protected and \
                   self.utc_offset == other.utc_offset and \
                   self.time_zone == other.time_zone and \
                   self.url == other.url and \
                   self.statuses_count == other.statuses_count and \
                   self.followers_count == other.followers_count and \
                   self.favourites_count == other.favourites_count and \
                   self.friends_count == other.friends_count and \
                   self.status == other.status and \
                   self.geo_enabled == other.geo_enabled and \
                   self.verified == other.verified and \
                   self.lang == other.lang and \
                   self.notifications == other.notifications and \
                   self.contributors_enabled == other.contributors_enabled and \
                   self.created_at == other.created_at and \
                   self.listed_count == other.listed_count

        except AttributeError:
            return False

    def __str__(self):
        """A string representation of this twitter.User instance.

        The return value is the same as the JSON string representation.

        Returns:
          A string representation of this twitter.User instance.
        """
        return self.AsJsonString()

    def AsJsonString(self):
        """A JSON string representation of this twitter.User instance.

        Returns:
          A JSON string representation of this twitter.User instance
       """
        return json.dumps(self.AsDict(), sort_keys=True)

    def AsDict(self):
        """A dict representation of this twitter.User instance.

        The return value uses the same key names as the JSON representation.

        Return:
          A dict representing this twitter.User instance
        """
        data = {}
        if self.id:
            data['id'] = self.id
        if self.name:
            data['name'] = self.name
        if self.screen_name:
            data['screen_name'] = self.screen_name
        if self.location:
            data['location'] = self.location
        if self.description:
            data['description'] = self.description
        if self.default_profile:
            data['default_profile'] = self.default_profile
        if self.default_profile_image:
            data['default_profile_image'] = self.default_profile_image
        if self.profile_image_url:
            data['profile_image_url'] = self.profile_image_url
        if self.profile_background_tile is not None:
            data['profile_background_tile'] = self.profile_background_tile
        if self.profile_background_image_url:
            data['profile_background_image_url'] = self.profile_background_image_url
        if self.profile_banner_url:
            data['profile_banner_url'] = self.profile_banner_url
        if self.profile_sidebar_fill_color:
            data['profile_sidebar_fill_color'] = self.profile_sidebar_fill_color
        if self.profile_background_color:
            data['profile_background_color'] = self.profile_background_color
        if self.profile_link_color:
            data['profile_link_color'] = self.profile_link_color
        if self.profile_text_color:
            data['profile_text_color'] = self.profile_text_color
        if self.protected is not None:
            data['protected'] = self.protected
        if self.utc_offset:
            data['utc_offset'] = self.utc_offset
        if self.time_zone:
            data['time_zone'] = self.time_zone
        if self.url:
            data['url'] = self.url
        if self.status:
            data['status'] = self.status.AsDict()
        if self.friends_count:
            data['friends_count'] = self.friends_count
        if self.followers_count:
            data['followers_count'] = self.followers_count
        if self.statuses_count:
            data['statuses_count'] = self.statuses_count
        if self.favourites_count:
            data['favourites_count'] = self.favourites_count
        if self.geo_enabled:
            data['geo_enabled'] = self.geo_enabled
        if self.verified:
            data['verified'] = self.verified
        if self.lang:
            data['lang'] = self.lang
        if self.notifications:
            data['notifications'] = self.notifications
        if self.contributors_enabled:
            data['contributors_enabled'] = self.contributors_enabled
        if self.created_at:
            data['created_at'] = self.created_at
        if self.listed_count:
            data['listed_count'] = self.listed_count

        return data

    @staticmethod
    def NewFromJsonDict(data):
        """Create a new instance based on a JSON dict.

        Args:
          data:
            A JSON dict, as converted from the JSON in the twitter API

        Returns:
          A twitter.User instance
        """
        if 'status' in data:
            from twitter import Status
            # Have to do the import here to prevent cyclic imports
            # in the __init__.py file
            status = Status.NewFromJsonDict(data['status'])
        else:
            status = None
        return User(id=data.get('id', None),
                    name=data.get('name', None),
                    screen_name=data.get('screen_name', None),
                    location=data.get('location', None),
                    description=data.get('description', None),
                    statuses_count=data.get('statuses_count', None),
                    followers_count=data.get('followers_count', None),
                    favourites_count=data.get('favourites_count', None),
                    default_profile=data.get('default_profile', None),
                    default_profile_image=data.get('default_profile_image', None),
                    friends_count=data.get('friends_count', None),
                    profile_image_url=data.get('profile_image_url_https', data.get('profile_image_url', None)),
                    profile_background_tile=data.get('profile_background_tile', None),
                    profile_background_image_url=data.get('profile_background_image_url', None),
                    profile_banner_url=data.get('profile_banner_url', None),
                    profile_sidebar_fill_color=data.get('profile_sidebar_fill_color', None),
                    profile_background_color=data.get('profile_background_color', None),
                    profile_link_color=data.get('profile_link_color', None),
                    profile_text_color=data.get('profile_text_color', None),
                    protected=data.get('protected', None),
                    utc_offset=data.get('utc_offset', None),
                    time_zone=data.get('time_zone', None),
                    url=data.get('url', None),
                    status=status,
                    geo_enabled=data.get('geo_enabled', None),
                    verified=data.get('verified', None),
                    lang=data.get('lang', None),
                    notifications=data.get('notifications', None),
                    contributors_enabled=data.get('contributors_enabled', None),
                    created_at=data.get('created_at', None),
                    listed_count=data.get('listed_count', None))
