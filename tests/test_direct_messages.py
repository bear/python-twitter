#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import re

import twitter

import responses
from responses import GET, POST

DEFAULT_BASE_URL = re.compile(r'https?://api\.twitter.com/1\.1/.*')
DEFAULT_UPLOAD_URL = re.compile(r'https?://upload\.twitter.com/1\.1/.*')

global api
api = twitter.Api('test', 'test', 'test', 'test', tweet_mode='extended')


@responses.activate
def test_get_direct_messages():
    with open('testdata/direct_messages/get_direct_messages.json') as f:
        resp_data = f.read()
    responses.add(GET, DEFAULT_BASE_URL, body=resp_data)

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
    responses.add(GET, DEFAULT_BASE_URL, body=resp_data)

    resp = api.GetSentDirectMessages(count=1, page=1)
    direct_message = resp[0]
    assert isinstance(resp, list)
    assert isinstance(direct_message, twitter.DirectMessage)
    assert direct_message.id == 678629283007303683


@responses.activate
def test_post_direct_message():
    with open('testdata/direct_messages/post_post_direct_message.json', 'r') as f:
        responses.add(POST, DEFAULT_BASE_URL, body=f.read())
    resp = api.PostDirectMessage(user_id='372018022',
                                 text='hello')
    assert isinstance(resp, twitter.DirectMessage)
    assert resp.text == 'hello'


@responses.activate
def test_post_direct_message_with_media():
    with open('testdata/direct_messages/post_post_direct_message.json', 'r') as f:
        responses.add(POST, DEFAULT_BASE_URL, body=f.read())
    with open('testdata/post_upload_chunked_INIT.json') as f:
        responses.add(POST, DEFAULT_UPLOAD_URL, body=f.read())

    resp = api.PostDirectMessage(user_id='372018022',
                                 text='hello',
                                 media_file_path='testdata/media/happy.jpg',
                                 media_type='dm_image')
    assert isinstance(resp, twitter.DirectMessage)
    assert resp.text == 'hello'


@responses.activate
def test_destroy_direct_message():
    with open('testdata/direct_messages/post_destroy_direct_message.json', 'r') as f:
        responses.add(POST, DEFAULT_BASE_URL, body=f.read())
    resp = api.DestroyDirectMessage(message_id=855194351294656515)

    assert isinstance(resp, twitter.DirectMessage)
    assert resp.id == 855194351294656515
