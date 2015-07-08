from __future__ import absolute_import, print_function

__author__ = 'Lachlan'

import os
import tweepy
from tweepy.streaming import StreamListener
from tweepy import Stream
import json
from Flask_App.utils.processutils import (geolocate, process_names,
                                          location_to_names)
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
    def on_data(self, data):
        a = json.loads(data)
        #if a['coordinates'] == None:
        person = data
        twitter_handle = '@' + a['user']['screen_name']
        location = a['text']
        location = location.split()
        location.remove('@FieldGuideAU')
        location = ' '.join(location)
        try:
            lat, lng = geolocate(location)
        except TypeError:
            message = ("Sorry, we couldn't find your geolocation :(. Maybe"
                       " try type it like you would on googlemaps.")
            send_tweet(twitter_handle, message)
            return

        name_list = location_to_names(lat, lng)

        if not name_list:
            message = ("Sorry, we couldn't find any animals in your area :( "
                       "are you sure you location is in Australia?")
            send_tweet(twitter_handle, message)
            return

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
        message = ("Hey, here's your fieldguide for {0}. {1}"
                   .format(location, url))

        send_tweet(twitter_handle, message)

    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    l = StdOutListener()
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

    stream = Stream(auth, l)
    stream.filter(track=['@FieldGuideAU'])
