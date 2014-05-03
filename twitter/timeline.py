#!/usr/bin/env python

from calendar import timegm
import rfc822

from twitter import simplejson, TwitterError

class Timeline(object):
  '''A class representing the Timeline structure used by the twitter API.

  The Timeline structure exposes the following properties:

    timeline.id
    timeline.name
    timeline.slug
    timeline.description
    timeline.full_name
    timeline.mode
    timeline.uri
    timeline.member_count
    timeline.subscriber_count
    timeline.following
  '''
  def __init__(self, **kwargs):
    param_defaults = {
      'id':             None,
      'name':             None,
      'description':      None,
      'uri':              None,
      'user':             None}

    for (param, default) in param_defaults.iteritems():
      setattr(self, param, kwargs.get(param, default))

  def GetId(self):
    '''Get the unique id of this timeline.

    Returns:
      The unique id of this timeline
    '''
    return self._id

  def SetId(self, id):
    '''Set the unique id of this timeline.

    Args:
      id:
        The unique id of this timeline.
    '''
    self._id = id

  id = property(GetId, SetId,
                doc='The unique id of this timeline.')

  def GetName(self):
    '''Get the real name of this timeline.

    Returns:
      The real name of this timeline
    '''
    return self._name

  def SetName(self, name):
    '''Set the real name of this timeline.

    Args:
      name:
        The real name of this timeline
    '''
    self._name = name

  name = property(GetName, SetName,
                  doc='The real name of this timeline.')

  def GetDescription(self):
    '''Get the description of this timeline.

    Returns:
      The description of this timeline
    '''
    return self._description

  def SetDescription(self, description):
    '''Set the description of this timeline.

    Args:
      description:
        The description of this timeline.
    '''
    self._description = description

  description = property(GetDescription, SetDescription,
                         doc='The description of this timeline.')

  def GetUri(self):
    '''Get the uri of this timeline.

    Returns:
      The uri of this timeline
    '''
    return self._uri

  def SetUri(self, uri):
    '''Set the uri of this timeline.

    Args:
      uri:
        The uri of this timeline.
    '''
    self._uri = uri

  uri = property(GetUri, SetUri,
                 doc='The uri of this timeline.')

  def GetUser(self):
    '''Get the user of this timeline.

    Returns:
      The owner of this timeline
    '''
    return self._user

  def SetUser(self, user):
    '''Set the user of this timeline.

    Args:
      user:
        The owner of this timeline.
    '''
    self._user = user

  user = property(GetUser, SetUser,
                  doc='The owner of this timeline.')

  def __ne__(self, other):
    return not self.__eq__(other)

  def __eq__(self, other):
    try:
      return other and \
             self.id == other.id and \
             self.name == other.name and \
             self.description == other.description and \
             self.uri == other.uri and \
             self.user == other.user

    except AttributeError:
      return False

  def __str__(self):
    '''A string representation of this twitter.Timeline instance.

    The return value is the same as the JSON string representation.

    Returns:
      A string representation of this twitter.Timeline instance.
    '''
    return self.AsJsonString()

  def AsJsonString(self):
    '''A JSON string representation of this twitter.Timeline instance.

    Returns:
      A JSON string representation of this twitter.Timeline instance
   '''
    return simplejson.dumps(self.AsDict(), sort_keys=True)

  def AsDict(self):
    '''A dict representation of this twitter.Timeline instance.

    The return value uses the same key names as the JSON representation.

    Return:
      A dict representing this twitter.Timeline instance
    '''
    data = {}
    # if self.id:
    #   data['id'] = self.id
    if self.name:
      data['name'] = self.name
    if self.description:
      data['description'] = self.description
    if self.uri:
      data['custom_timeline_url'] = self.uri
    if self.user is not None:
      data['user_id'] = self.user
    return {self.id : data}

  @staticmethod
  def NewFromJsonDict(id, data):
    '''Create a new instance based on a JSON dict.

    Args:
      data:
        A JSON dict, as converted from the JSON in the twitter API

    Returns:
      A twitter.Timeline instance
    '''

    # if 'user' in data:
    #   user = User.NewFromJsonDict(data['user'])
    # else:
    #   user = None

    return Timeline(id=id,
                name=data.get('name', None),
                description=data.get('description', None),
                uri=data.get('custom_timeline_url', None),
                user=data.get('user_id', None))

