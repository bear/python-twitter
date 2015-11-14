#!/usr/bin/env python


class Category(object):
    """A class representing the suggested user category structure used by the twitter API.

    The UserStatus structure exposes the following properties:

      category.name
      category.slug
      category.size
    """

    def __init__(self, **kwargs):
        """An object to hold a Twitter suggested  user category .
        This class is normally instantiated by the twitter.Api class and
        returned in a sequence.

        Args:
          name:
            name of the category
          slug:

          size:
        """
        param_defaults = {
            'name': None,
            'slug': None,
            'size': None,
        }

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    @property
    def Name(self):
        return self.name or False

    @property
    def Slug(self):
        return self.slug or False

    @property
    def Size(self):
        return self.size or False

    @staticmethod
    def NewFromJsonDict(data):
        """Create a new instance based on a JSON dict.

        Args:
          data: A JSON dict, as converted from the JSON in the twitter API
        Returns:
          A twitter.Category instance
        """

        return Category(name=data.get('name', None),
                        slug=data.get('slug', None),
                        size=data.get('size', None))
