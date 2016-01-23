import json


class TwitterModel(object):

    """ Base class from which all twitter models will inherit. """

    def __init__(self, **kwargs):
        self.param_defaults = {}

    def __str__(self):
        return self.AsJsonString()

    def __eq__(self, other):
        return other and \
            self.AsDict() == other.AsDict()

    def __ne__(self, other):
        return not self.__eq__(other)

    def AsJsonString(self):
        return json.dumps(self.AsDict(), sort_keys=True)

    def AsDict(self):
        data = {}
        for (key, value) in self.param_defaults.items():
            if getattr(getattr(self, key, None), 'AsDict', None):
                data[key] = getattr(self, key).AsDict()
            elif getattr(self, key, None):
                data[key] = getattr(self, key, None)
        return data

    @classmethod
    def NewFromJsonDict(cls, data, **kwargs):
        """ Create a new instance based on a JSON dict.

        Args:
            data: A JSON dict, as converted from the JSON in the twitter API

        Returns:
            A twitter.Media instance
        """

        if kwargs:
            for key, val in kwargs.items():
                data[key] = val

        return cls(**data)


class Media(TwitterModel):

    """A class representing the Media component of a tweet. """

    def __init__(self, **kwargs):
        self.param_defaults = {
            'id': None,
            'expanded_url': None,
            'display_url': None,
            'url': None,
            'media_url_https': None,
            'media_url': None,
            'type': None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "Media(ID={media_id}, Type={type}, DisplayURL='{url}')".format(
            media_id=self.id,
            type=self.type,
            url=self.display_url)


class List(TwitterModel):

    """A class representing the List structure used by the twitter API. """

    def __init__(self, **kwargs):
        self.param_defaults = {
            'id': None,
            'name': None,
            'slug': None,
            'description': None,
            'full_name': None,
            'mode': None,
            'uri': None,
            'member_count': None,
            'subscriber_count': None,
            'following': None,
            'user': None}

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

        if 'user' in kwargs:
            self.user = User.NewFromJsonDict(kwargs.get('user'))

    def __repr__(self):
        return "List(ID={list_id}, FullName={full_name}, Slug={slug}, User={user})".format(
            list_id=self.id,
            full_name=self.full_name,
            slug=self.slug,
            user=self.user.screen_name)


class Category(TwitterModel):

    """A class representing the suggested user category structure. """

    def __init__(self, **kwargs):
        self.param_defaults = {
            'name': None,
            'slug': None,
            'size': None,
        }

        for (param, default) in self.param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "Category(Name={name}, Slug={slug}, Size={size})".format(
            name=self.name,
            slug=self.slug,
            size=self.size)


class DirectMessage(TwitterModel):

    """A class representing a Direct Message. """

    def __init__(self, **kwargs):
        self.param_defaults = {
            'id': None,
            'created_at': None,
            'sender_id': None,
            'sender_screen_name': None,
            'recipient_id': None,
            'recipient_screen_name': None,
            'text': None}

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        if self.text and len(self.text) > 140:
            text = self.text[:140] + "[...]"
        else:
            text = self.text
        return "DirectMessage(ID={dm_id}, Sender={sender}, Time={time}, Text={text})".format(
            dm_id=self.id,
            sender=self.sender_screen_name,
            time=self.created_at,
            text=text)


class Trend(TwitterModel):

    """ A class representing a trending topic. """

    def __init__(self, **kwargs):
        self.param_defaults = {
            'name': None,
            'query': None,
            'timestamp': None,
            'url': None}

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "Trend(Name={name}, Time={ts}, URL={url})".format(
            name=self.name,
            ts=self.timestamp,
            url=self.url)


class Hashtag(TwitterModel):

    """ A class representing a twitter hashtag. """

    def __init__(self, **kwargs):
        self.param_defaults = {
            'text': None
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "Hashtag(Text={text})".format(
            text=self.text)


class Url(TwitterModel):

    """ A class representing an URL contained in a tweet. """

    def __init__(self, **kwargs):
        self.param_defaults = {
            'url': None,
            'expanded_url': None}

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "URL(URL={url}, ExpandedURL={eurl})".format(
            url=self.url,
            eurl=self.expanded_url)


class UserStatus(TwitterModel):

    """ A class representing the UserStatus structure. This is an abbreviated
    form of the twitter.User object. """

    def __init__(self, **kwargs):
        self.param_defaults = {
            'name': None,
            'id': None,
            'id_str': None,
            'screen_name': None,
            'following': None,
            'followed_by': None}

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "UserStatus(ID={uid}, Name={sn}, Following={fng}, Followed={fed})".format(
            uid=self.id,
            sn=self.screen_name,
            fng=self.following,
            fed=self.followed_by)


class User(TwitterModel):

    """A class representing the User structure. """

    def __init__(self, **kwargs):
        self.param_defaults = {
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

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "User(ID={uid}, Screenname={sn})".format(
            uid=self.id,
            sn=self.screen_name)
