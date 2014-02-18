#!/usr/bin/env python

from twitter import TwitterError

class Hashtag(object):
  ''' A class representing a twitter hashtag
  '''
  def __init__(self,
               text=None):
    self.text = text

  @staticmethod
  def NewFromJsonDict(data):
    '''Create a new instance based on a JSON dict.

    Args:
      data:
        A JSON dict, as converted from the JSON in the twitter API

    Returns:
      A twitter.Hashtag instance
    '''
    return Hashtag(text=data.get('text', None))
