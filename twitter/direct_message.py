#!/usr/bin/env python

from calendar import timegm

try:
    from rfc822 import parsedate
except ImportError:
    from email.utils import parsedate

from twitter import json, TwitterError


class DirectMessage(object):
    """A class representing the DirectMessage structure used by the twitter API.

    The DirectMessage structure exposes the following properties:

      direct_message.id
      direct_message.created_at
      direct_message.created_at_in_seconds # read only
      direct_message.sender_id
      direct_message.sender_screen_name
      direct_message.recipient_id
      direct_message.recipient_screen_name
      direct_message.text
    """

    def __init__(self,
                 id=None,
                 created_at=None,
                 sender_id=None,
                 sender_screen_name=None,
                 recipient_id=None,
                 recipient_screen_name=None,
                 text=None):
        """An object to hold a Twitter direct message.

        This class is normally instantiated by the twitter.Api class and
        returned in a sequence.

        Note: Dates are posted in the form "Sat Jan 27 04:17:38 +0000 2007"

        Args:
          id:
            The unique id of this direct message. [Optional]
          created_at:
            The time this direct message was posted. [Optional]
          sender_id:
            The id of the twitter user that sent this message. [Optional]
          sender_screen_name:
            The name of the twitter user that sent this message. [Optional]
          recipient_id:
            The id of the twitter that received this message. [Optional]
          recipient_screen_name:
            The name of the twitter that received this message. [Optional]
          text:
            The text of this direct message. [Optional]
        """
        self.id = id
        self.created_at = created_at
        self.sender_id = sender_id
        self.sender_screen_name = sender_screen_name
        self.recipient_id = recipient_id
        self.recipient_screen_name = recipient_screen_name
        self.text = text

    # Functions that you should be able to set.

    @property
    def RecipientScreenName(self):
        """Get the unique recipient screen name of this direct message.

        Returns:
          The unique recipient screen name of this direct message
        """
        return self._recipient_screen_name

    @RecipientScreenName.setter
    def RecipientScreenName(self, recipient_screen_name):
        self._recipient_screen_name = recipient_screen_name

    @property
    def Text(self):
        """Get the text of this direct message.

        Returns:
          The text of this direct message.
        """
        return self._text

    @Text.setter
    def Text(self, text):
        self._text = text

    @property
    def RecipientId(self):
        """Get the unique recipient id of this direct message.

        Returns:
          The unique recipient id of this direct message
        """
        return self._recipient_id

    @RecipientId.setter
    def RecipientId(self, recipient_id):
        self._recipient_id = recipient_id

    # Functions that are only getters.

    @property
    def Id(self):
        """Get the unique id of this direct message.

        Returns:
          The unique id of this direct message
        """
        return self._id

    @property
    def CreatedAt(self):
        """Get the time this direct message was posted.

        Returns:
          The time this direct message was posted
        """
        return self._created_at

    @property
    def CreatedAtInSeconds(self):
        """Get the time this direct message was posted, in seconds since the epoch.

        Returns:
          The time this direct message was posted, in seconds since the epoch.
        """
        return timegm(rfc822.parsedate(self.created_at))

    @property
    def SenderScreenName(self):
        """Get the unique sender screen name of this direct message.

        Returns:
          The unique sender screen name of this direct message
        """
        return self._sender_screen_name

    @property
    def SenderId(self):
        """Get the unique sender id of this direct message.

        Returns:
          The unique sender id of this direct message
        """
        return self._sender_id


    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        try:
            return other and \
                   self.id == other.id and \
                   self.created_at == other.created_at and \
                   self.sender_id == other.sender_id and \
                   self.sender_screen_name == other.sender_screen_name and \
                   self.recipient_id == other.recipient_id and \
                   self.recipient_screen_name == other.recipient_screen_name and \
                   self.text == other.text
        except AttributeError:
            return False

    def __str__(self):
        """A string representation of this twitter.DirectMessage instance.

        The return value is the same as the JSON string representation.

        Returns:
          A string representation of this twitter.DirectMessage instance.
        """
        return self.AsJsonString()

    def AsJsonString(self):
        """A JSON string representation of this twitter.DirectMessage instance.

        Returns:
          A JSON string representation of this twitter.DirectMessage instance
       """
        return json.dumps(self.AsDict(), sort_keys=True)

    def AsDict(self):
        """A dict representation of this twitter.DirectMessage instance.

        The return value uses the same key names as the JSON representation.

        Return:
          A dict representing this twitter.DirectMessage instance
        """
        data = {}
        if self.id:
            data['id'] = self.id
        if self.created_at:
            data['created_at'] = self.created_at
        if self.sender_id:
            data['sender_id'] = self.sender_id
        if self.sender_screen_name:
            data['sender_screen_name'] = self.sender_screen_name
        if self.recipient_id:
            data['recipient_id'] = self.recipient_id
        if self.recipient_screen_name:
            data['recipient_screen_name'] = self.recipient_screen_name
        if self.text:
            data['text'] = self.text
        return data

    @staticmethod
    def NewFromJsonDict(data):
        """Create a new instance based on a JSON dict.

        Args:
          data:
            A JSON dict, as converted from the JSON in the twitter API

        Returns:
          A twitter.DirectMessage instance
        """
        return DirectMessage(created_at=data.get('created_at', None),
                             recipient_id=data.get('recipient_id', None),
                             sender_id=data.get('sender_id', None),
                             text=data.get('text', None),
                             sender_screen_name=data.get('sender_screen_name', None),
                             id=data.get('id', None),
                             recipient_screen_name=data.get('recipient_screen_name', None))
