from __future__ import absolute_import, print_function

__author__ = 'Lachlan'

import os
import tweepy
from tweepy.streaming import StreamListener
from tweepy import Stream
import json
from Flask_App.utils.processutils import geolocate, process_names
from Flask_App.models.services.request_service import RequestService
from Flask_App.models.services.thing_service import ThingService
from Flask_App import db_session
import datetime
from Flask_App.utils.twitter_reply import send_tweet

#enter the corresponding information from your Twitter application:
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET'] 
ACCESS_KEY = os.environ['ACCESS_KEY']
ACCESS_SECRET = os.environ['ACCESS_SECRET']
HTTP_SERVER = os.environ.get('')

def parse(query):
    pass

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        a = json.loads(data)
        #if a['coordinates'] == None:
        person = data
        twitter_handle = '@' + a['user']['screen_name']
        location = a['text']
        location = location.split()
        location.remove('@FieldGuideAU')
        location = ' '.join(location)
        # lat, lng = geolocate(geoloc)
        name_list = {'Kookaburra': 'Dacelo novaeguineae',
                     'Emu': 'Dromaius novaehollandiae',
                     'Little Penguin': 'Eudyptula minor',
                     'Lyrebird': 'Menura novaehollandiae',
                     'King Parrot': 'Alisterus scapularis',
                     "Southern Cassowary": "Casuarius casuarius"}

        data = process_names(name_list)

        user = {'time': datetime.datetime.now(), 'person': person}
        req_service = RequestService(db_session)
        thing_service = ThingService(db_session)

        user_resp = req_service.create(**user)
        for animal in data.values():
            animal['request'] = user_resp
            thing_service.create(**dict(animal))
        uuid = user_resp.uuid
        url = "https://fieldguideau.herokuapp.com/request/{0}".format(uuid)
        message = "Hey, here's your fieldguide for {0}. {1}"\
            .format(location, url)

        send_tweet(twitter_handle, message)

    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    l = StdOutListener()
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

    stream = Stream(auth, l)
    stream.filter(track=['@FieldGuideAU'])
