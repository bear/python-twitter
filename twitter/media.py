#!/usr/bin/env python


class Media(object):
    """A class representing the Media component of a tweet.

    The Media structure exposes the following properties:

      media.expanded_url
      media.display_url
      media.url
      media.media_url_https
      media.media_url
      media.type
    """

    def __init__(self, **kwargs):
        """An object to the information for each Media entity for a tweet
        This class is normally instantiated by the twitter.Api class and
        returned in a sequence.
        """
        param_defaults = {
            'expanded_url': None,
            'display_url': None,
            'url': None,
            'media_url_https': None,
            'media_url': None,
            'type': None,
            'variants': None
        }

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    @property
    def Expanded_url(self):
        return self.expanded_url or False

    @property
    def Url(self):
        return self.url or False

    @property
    def Media_url_https(self):
        return self.media_url_https or False

    @property
    def Media_url(self):
        return self.media_url or False

    @property
    def Type(self):
        return self.type or False

    @property
    def Variants(self):
        return self.variants or False

    def __eq__(self, other):
        return other.Media_url == self.Media_url and other.Type == self.Type

    def __hash__(self):
        return hash((self.Media_url, self.Type))

    def AsDict(self):
        """A dict representation of this twitter.Media instance.

        The return value uses the same key names as the JSON representation.

        Return:
          A dict representing this twitter.Media instance
        """
        data = {}
        if self.expanded_url:
            data['expanded_url'] = self.expanded_url
        if self.display_url:
            data['display_url'] = self.display_url
        if self.url:
            data['url'] = self.url
        if self.media_url_https:
            data['media_url_https'] = self.media_url_https
        if self.media_url:
            data['media_url'] = self.media_url
        if self.type:
            data['type'] = self.type
        if self.variants:
            data['variants'] = self.variants
        return data

    @staticmethod
    def NewFromJsonDict(data):
        """Create a new instance based on a JSON dict.

        Args:
          data: A JSON dict, as converted from the JSON in the twitter API
        Returns:
          A twitter.Media instance
        """
        variants = None
        if 'video_info' in data:
            variants = data['video_info']['variants']

        return Media(expanded_url=data.get('expanded_url', None),
                     display_url=data.get('display_url', None),
                     url=data.get('url', None),
                     media_url_https=data.get('media_url_https', None),
                     media_url=data.get('media_url', None),
                     type=data.get('type', None),
                     variants=variants
                     )
