#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import json
import os
import re
import sys
from tempfile import NamedTemporaryFile
import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
import warnings

import twitter

import responses
from responses import GET, POST

DEFAULT_URL = re.compile(r'https?://.*\.twitter.com/1\.1/.*')

global api
api = twitter.Api('test', 'test', 'test', 'test', tweet_mode='extended')


@responses.activate
def test_get_direct_messages():
    with open('testdata/direct_messages/get_direct_messages.json') as f:
        resp_data = f.read()
    responses.add(GET, DEFAULT_URL, body=resp_data)

    resp = api.GetDirectMessages(count=1, page=1)
    direct_message = resp[0]
    assert isinstance(resp, list)
    assert isinstance(direct_message, twitter.DirectMessage)
    assert direct_message.id == 678629245946433539

    try:
        resp = api.GetDirectMessages(count='asdf')
        assert 0
    except twitter.TwitterError as e:
        assert True


@responses.activate
def test_get_sent_direct_messages():
    with open('testdata/direct_messages/get_sent_direct_messages.json') as f:
        resp_data = f.read()
    responses.add(GET, DEFAULT_URL, body=resp_data)

    resp = api.GetSentDirectMessages(count=1, page=1)
    direct_message = resp[0]
    assert isinstance(resp, list)
    assert isinstance(direct_message, twitter.DirectMessage)
    assert direct_message.id == 678629283007303683


@responses.activate
def test_post_direct_message():
    with open('testdata/direct_messages/post_post_direct_message.json', 'r') as f:
        responses.add(POST, DEFAULT_URL, body=f.read())
    resp = api.PostDirectMessage(user_id='372018022',
                                 text='https://t.co/L4MIplKUwR')
    assert isinstance(resp, twitter.DirectMessage)
    assert resp.text == 'https://t.co/L4MIplKUwR'


@responses.activate
def test_destroy_direct_message():
    with open('testdata/direct_messages/post_destroy_direct_message.json', 'r') as f:
        responses.add(POST, DEFAULT_URL, body=f.read())
    resp = api.DestroyDirectMessage(message_id=855194351294656515)

    assert isinstance(resp, twitter.DirectMessage)
    assert resp.id == 855194351294656515
