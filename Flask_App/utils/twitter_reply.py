__author__ = 'Lachlan'

import tweepy, os


#enter the corresponding information from your Twitter application:
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_KEY = os.environ['ACCESS_KEY']
ACCESS_SECRET = os.environ['ACCESS_SECRET']

class TwitterError(Exception):
    pass

def send_tweet(twitter_handle, message):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    try:
        message_str = '{0} {1}'.format(twitter_handle, message)
        api.update_status(status=message_str)
    except Exception as e:
        raise TwitterError(e)
