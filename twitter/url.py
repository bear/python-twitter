#!/usr/bin/env python

from twitter import TwitterError

class Url(object):
  '''A class representing an URL contained in a tweet'''
  def __init__(self,
               url=None,
               expanded_url=None):
    self.url = url
    self.expanded_url = expanded_url

  @staticmethod
  def NewFromJsonDict(data):
    '''Create a new instance based on a JSON dict.

    Args:
      data:
        A JSON dict, as converted from the JSON in the twitter API

    Returns:
      A twitter.Url instance
    '''
    return Url(url=data.get('url', None),
               expanded_url=data.get('expanded_url', None))
