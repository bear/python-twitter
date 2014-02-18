#!/usr/bin/env python

from twitter import TwitterError

class Trend(object):
  ''' A class representing a trending topic
  '''
  def __init__(self, name=None, query=None, timestamp=None, url=None):
    self.name = name
    self.query = query
    self.timestamp = timestamp
    self.url = url

  def __repr__(self):
    return self.name

  def __str__(self):
    return 'Name: %s\nQuery: %s\nTimestamp: %s\nSearch URL: %s\n' % (self.name, self.query, self.timestamp, self.url)

  def __ne__(self, other):
    return not self.__eq__(other)

  def __eq__(self, other):
    try:
      return other and \
          self.name == other.name and \
          self.query == other.query and \
          self.timestamp == other.timestamp and \
          self.url == self.url
    except AttributeError:
      return False

  @staticmethod
  def NewFromJsonDict(data, timestamp=None):
    '''Create a new instance based on a JSON dict

    Args:
      data:
        A JSON dict
      timestamp:
        Gets set as the timestamp property of the new object

    Returns:
      A twitter.Trend object
    '''
    return Trend(name=data.get('name', None),
                 query=data.get('query', None),
                 url=data.get('url', None),
                 timestamp=timestamp)
