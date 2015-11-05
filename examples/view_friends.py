import twitter

api = twitter.Api(consumer_key='consumer_key',
                  consumer_secret='consumer_secret',
                  access_token_key='access_token',
                  access_token_secret='access_token_secret')
users = api.GetFriends()
print [u.name for u in users]
