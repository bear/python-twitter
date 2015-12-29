#!/usr/bin/env python

from twitter import json, User


class List(object):
    """A class representing the List structure used by the twitter API.

    The List structure exposes the following properties:

      list.id
      list.name
      list.slug
      list.description
      list.full_name
      list.mode
      list.uri
      list.member_count
      list.subscriber_count
      list.following
    """

    def __init__(self, **kwargs):
        param_defaults = {
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

        for (param, default) in param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    @property
    def Id(self):
        """Get the unique id of this list.

        Returns:
          The unique id of this list
        """
        return self._id

    @property
    def Name(self):
        """Get the real name of this list.

        Returns:
          The real name of this list
        """
        return self._name

    @property
    def Slug(self):
        """Get the slug of this list.

        Returns:
          The slug of this list
        """
        return self._slug

    @property
    def Description(self):
        """Get the description of this list.

        Returns:
          The description of this list
        """
        return self._description

    @property
    def Full_name(self):
        """Get the full_name of this list.

        Returns:
          The full_name of this list
        """
        return self._full_name

    @property
    def Mode(self):
        """Get the mode of this list.

        Returns:
          The mode of this list
        """
        return self._mode

    @property
    def Uri(self):
        """Get the uri of this list.

        Returns:
          The uri of this list
        """
        return self._uri

    @property
    def Member_count(self):
        """Get the member_count of this list.

        Returns:
          The member_count of this list
        """
        return self._member_count

    @property
    def Subscriber_count(self):
        """Get the subscriber_count of this list.

        Returns:
          The subscriber_count of this list
        """
        return self._subscriber_count

    @property
    def Following(self):
        """Get the following status of this list.

        Returns:
          The following status of this list
        """
        return self._following

    @property
    def User(self):
        """Get the user of this list.

        Returns:
          The owner of this list
        """
        return self._user

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        try:
            return other and \
                   self.id == other.id and \
                   self.name == other.name and \
                   self.slug == other.slug and \
                   self.description == other.description and \
                   self.full_name == other.full_name and \
                   self.mode == other.mode and \
                   self.uri == other.uri and \
                   self.member_count == other.member_count and \
                   self.subscriber_count == other.subscriber_count and \
                   self.following == other.following and \
                   self.user == other.user

        except AttributeError:
            return False

    def __str__(self):
        """A string representation of this twitter.List instance.

        The return value is the same as the JSON string representation.

        Returns:
          A string representation of this twitter.List instance.
        """
        return self.AsJsonString()

    def AsJsonString(self):
        """A JSON string representation of this twitter.List instance.

        Returns:
          A JSON string representation of this twitter.List instance
       """
        return json.dumps(self.AsDict(), sort_keys=True)

    def AsDict(self):
        """A dict representation of this twitter.List instance.

        The return value uses the same key names as the JSON representation.

        Return:
          A dict representing this twitter.List instance
        """
        data = {}
        if self.id:
            data['id'] = self.id
        if self.name:
            data['name'] = self.name
        if self.slug:
            data['slug'] = self.slug
        if self.description:
            data['description'] = self.description
        if self.full_name:
            data['full_name'] = self.full_name
        if self.mode:
            data['mode'] = self.mode
        if self.uri:
            data['uri'] = self.uri
        if self.member_count is not None:
            data['member_count'] = self.member_count
        if self.subscriber_count is not None:
            data['subscriber_count'] = self.subscriber_count
        if self.following is not None:
            data['following'] = self.following
        if self.user is not None:
            data['user'] = self.user.AsDict()
        return data

    @staticmethod
    def NewFromJsonDict(data):
        """Create a new instance based on a JSON dict.

        Args:
          data:
            A JSON dict, as converted from the JSON in the twitter API

        Returns:
          A twitter.List instance
        """
        if 'user' in data:
            user = User.NewFromJsonDict(data['user'])
        else:
            user = None
        return List(id=data.get('id', None),
                    name=data.get('name', None),
                    slug=data.get('slug', None),
                    description=data.get('description', None),
                    full_name=data.get('full_name', None),
                    mode=data.get('mode', None),
                    uri=data.get('uri', None),
                    member_count=data.get('member_count', None),
                    subscriber_count=data.get('subscriber_count', None),
                    following=data.get('following', None),
                    user=user)
