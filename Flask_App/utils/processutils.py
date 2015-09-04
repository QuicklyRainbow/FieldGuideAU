__author__ = 'mitch, eric'
import logging
import wikipedia
import urllib3.contrib.pyopenssl
import flickrapi
import flickrapi.shorturl
import googlemaps
import gevent
import gevent.monkey
from pyteaser import Summarize
from settings import FLICKR_API, FLICKR_API_SECRET, GOOGLEMAPS_API
from collections import defaultdict
import requests
import random



gevent.monkey.patch_socket()

# https fix https://urllib3.readthedocs.org/en/latest/security.html#pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

def wiki_summary(name):
    try:
        page = wikipedia.page(name)
        summary = wikipedia.summary(name, sentences=20)
        url = page.url
        output = Summarize(page.title, summary)
        return name, url, ' '.join(output)
    except wikipedia.PageError:
        logging.warning("No wiki entry for '{0}'.".format(name))
        return None

def flickr_pic(name, short_url=False):
    flickr = flickrapi.FlickrAPI(FLICKR_API, FLICKR_API_SECRET)
    for photo in flickr.walk(tags=name+',australia', safe_search=1, media='photos',
                             per_page=1, sort="relevance", tag_mode='all'):

        if short_url:
            return flickrapi.shorturl.url(photo.get('id'))
        else:
            return (name, "https://farm{0}.staticflickr.com/{1}/{2}_{3}.jpg"
                    .format(photo.get('farm'), photo.get('server'),
                            photo.get('id'), photo.get('secret')))


def geolocate(address):
    gmaps = googlemaps.Client(key=GOOGLEMAPS_API)
    try:
        result = gmaps.geocode(address, region='AU')
        lat = result[0]['geometry']['location']['lat']
        lng = result[0]['geometry']['location']['lng']
    except IndexError:
        logging.warning("Couldn't find location: {0}".format(address))
        return None
    else:
        return lat, lng

def process_names(name_list):
    output_dict = defaultdict(defaultdict)
    threads = []
    for name in name_list.keys():
        threads.append(gevent.spawn(wiki_summary, name))
    gevent.joinall(threads)
    for name_object in threads:
        try:
            output_dict[name_object.value[0]]['description'] = name_object.value[2]
            output_dict[name_object.value[0]]['description_url'] = name_object.value[1]
            output_dict[name_object.value[0]]['image_url'] = flickr_pic(name_list[name_object.value[0]])[1]
            output_dict[name_object.value[0]]['name'] = name_object.value[0]
        except Exception as e:
            if name_object.value is None:
                logging.warning("Couldn't retrive some weird animal, skipping."
                                " Error: {0}".format(e))
            else:
                output_dict.pop(name_object.value[0])
                logging.warning("Couldn't retrive {0}, skipping. Error: {1}"
                                .format(name_object.value[0], e))
    return output_dict

def location_to_names(lat, lng, radius=1, animals=None):
    if animals is None:
        animals = {}

    radius_limit = 16
    minimum_to_show = 6
    maximum_to_show = 8
    if radius > radius_limit:
        return animals
    payload = requests.get("http://biocache.ala.org.au/ws/occurrences/search?"
                           "lat={0}&lon={1}&radius={2}&facet=OFF"
                           .format(lat, lng, radius))
    for animal in payload.json()['occurrences']:
        if len(animals) >= maximum_to_show:
            break
        if 'vernacularName' in animal and 'scientificName' in animal and random.randint(0, 1) is 1:
            animals[animal['vernacularName']] = animal['scientificName']
    if len(animals) >= minimum_to_show:
        return animals
    else:
        return location_to_names(lat, lng, radius*2, animals)
