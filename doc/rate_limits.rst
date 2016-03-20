Rate Limiting
-------------

Overview
++++++++

Twitter imposes rate limiting based either on user tokens or application
tokens. Please see: `API Rate Limits
<https://dev.twitter.com/rest/public/rate-limiting>`_ for a more detailed
explanation of Twitter's policies. What follows will be a summary of how Python-Twitter attempts to
deal with rate limits and how you should expect those limits to be respected
(or not).


Python-Twitter tries to abstract away the details of Twitter's rate limiting by
allowing you to globally respect those limits or ignore them. If you wish to
have the application sleep when it hits a rate limit, you should instantiate
the API with ``sleep_on_rate_limit=True`` like so::

    import twitter
    api = twitter.Api(consumer_key=[consumer key],
                      consumer_secret=[consumer secret],
                      access_token_key=[access token],
                      access_token_secret=[access token secret],
                      sleep_on_rate_limit=True)

**By default, python-twitter will raise a hard error for rate limits**

Effectively, when the API determines that the **next** call to an endpoint will
result in a rate limit error being thrown by Twitter, it will sleep until you
are able to safely make that call. For most API methods, the headers in the
response from Twitter will contain the following information:

    ``x-rate-limit-limit``: The number of times you can request the given
    endpoint within a certain number of minutes (otherwise known as a window).

    ``x-rate-limit-remaining``: The number of times you have left for a given endpoint within a window.

    ``x-rate-limit-reset``: The number of seconds left until the window resets.

For most endpoints, this is 15 requests per 15 minutes. So if you have set the
global ``sleep_on_rate_limit`` to ``True``, the process looks something like this::

    api.GetListMembersPaged()
    # GET /list/{id}/members.json?cursor=-1
    # GET /list/{id}/members.json?cursor=2
    # GET /list/{id}/members.json?cursor=3
    # GET /list/{id}/members.json?cursor=4
    # GET /list/{id}/members.json?cursor=5
    # GET /list/{id}/members.json?cursor=6
    # GET /list/{id}/members.json?cursor=7
    # GET /list/{id}/members.json?cursor=8
    # GET /list/{id}/members.json?cursor=9
    # GET /list/{id}/members.json?cursor=10
    # GET /list/{id}/members.json?cursor=11
    # GET /list/{id}/members.json?cursor=12
    # GET /list/{id}/members.json?cursor=13
    # GET /list/{id}/members.json?cursor=14
    
    # This last GET request returns a response where x-rate-limit-remaining
    # is equal to 0, so the API sleeps for 15 minutes

    # GET /list/{id}/members.json?cursor=15

    # ... etc ...

If you would rather not have your API instance sleep when hitting, then do not
pass ``sleep_on_rate_limit=True`` to your API instance. This will cause the API
to raise a hard error when attempting to make call #15 above.

Technical
+++++++++

The ``twitter/ratelimit.py`` file contains the code that handles storing and
checking rate limits for endpoints. Since Twitter does not send any information
regarding the endpoint that you are requesting with the ``x-rate-limit-*``
headers, the endpoint is determined by some regex using the URL.

The twitter.Api instance contains an ``Api.rate_limit`` object that you can inspect
to see the current limits for any URL and exposes a number of methods for
querying and setting rate limits on a per-resource (i.e., endpoint) basis. See
:py:func:`twitter.ratelimit.RateLimit` for more information.

