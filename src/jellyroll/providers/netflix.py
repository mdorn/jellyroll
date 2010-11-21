"""
Provider for Netflix user history. Currently gets recently returned DVDs.

Currently requires creation of Netflix API tokens for settings.py 
using ``./manage.py jellyroll_netflix_tokens``. Set ``NETFLIX_CONSUMER_KEY``
and ``NETFLIX_CONSUMER_SECRET`` from your Netflix API account and then run.

Required settings.py values:

    * ``NETFLIX_CONSUMER_KEY``
    * ``NETFLIX_CONSUMER_SECRET``
    * ``NETFLIX_OAUTH_TOKEN``
    * ``NETFLIX_OAUTH_TOKEN_SECRET``

Optional settings.py values:

    * ``NETFLIX_TAG_ALL``: a string that all items will be tagged with (eg. "film")
    * ``NETFLIX_TAGS_FROM_CATEGORIES`` -- boolean indicating whether to create tags
      from Netflix categories
    * ``NETFLIX_TAG_PROCESSOR``: a function that takes a list of Netflix categories
      (e.g. ``["Foreign Art-House Thrillers", "German Language"]``) and returns a list
      of tags created by your function's custom logic.
"""
from datetime import datetime
import hashlib
import logging
import time 
import urlparse, urllib
import oauth2 as oauth
import time

from django.conf import settings
from django.db import transaction
from django.utils.encoding import smart_str, smart_unicode

from jellyroll.models import Purchase, Item
from jellyroll.providers import utils

log = logging.getLogger("jellyroll.providers.netflix")

class NetflixError(Exception):
    def __init__(self, code, message):
        self.code, self.message = code, message
    def __str__(self):
        return 'NetflixError %s: %s' % (self.code, self.message)

class NetflixClient(object):
    '''
    A mini Netflix API client
    '''
    updated_min = None
    
    def __init__(self, oauth_token, oauth_token_secret, updated_min, method='users'):
        self.method = method
        if self.method == 'users':
            self.method = 'users/%s' % oauth_token
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.updated_min = updated_min
       
    def __getattr__(self, method):
        return NetflixClient(self.oauth_token, self.oauth_token_secret, self.updated_min, '%s/%s' % (self.method, method))
       
    def __call__(self, **params):
        url = 'http://api.netflix.com/%s' % self.method
        return self._make_request(url)
    
    def _make_request(self, api_endpoint):
        params = {
            'oauth_token': self.oauth_token,
            'oauth_consumer_key': settings.NETFLIX_CONSUMER_KEY,
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time()),
            'output': 'json',
            'max_results': '20' # up to 100 legally, but will give back more (200?)
        }
        if self.updated_min:
            params['updated_min'] = self.updated_min
        consumer = oauth.Consumer(settings.NETFLIX_CONSUMER_KEY, settings.NETFLIX_CONSUMER_SECRET)
        token = oauth.Token(key=self.oauth_token, secret=self.oauth_token_secret)
        req = oauth.Request(method="GET", url=api_endpoint, parameters=params)
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, consumer, token)

        url = req.to_url()
        json = utils.getjson(url)
        if json.has_key('status'):
            raise NetflixError(json['status']['status_code'], json['status']['message'])
        return json

#
# Public API
#
def enabled():
    ok = (hasattr(settings, "NETFLIX_CONSUMER_KEY") and
          hasattr(settings, "NETFLIX_CONSUMER_SECRET"))
    if not ok:
      log.warn('The Netflix provider is not available because the '
               'NETFLIX_CONSUMER_KEY, and/or NETFLIX_CONSUMER_SECRET settings '
               'are undefined.')
    return ok

def update():
    # FIXME: below values should both be stored in/retrieved from DB
    oauth_token = settings.NETFLIX_OAUTH_TOKEN
    oauth_token_secret = settings.NETFLIX_OAUTH_TOKEN_SECRET

    last_update_date = Item.objects.get_last_update_of_model(Purchase, source=__name__)
    if last_update_date:
        last_update_epoch = int(time.mktime(last_update_date.timetuple())) + 1
        updated_min = last_update_epoch
    else:
        updated_min = None

    netflix = NetflixClient(oauth_token, oauth_token_secret, updated_min)
    results = netflix.rental_history.returned()
    
    if results['rental_history'].has_key('rental_history_item'):
        log.info('Processing %s results.' % results['rental_history']['number_of_results'])
        if isinstance(results['rental_history']['rental_history_item'], dict):
            items = [results['rental_history']['rental_history_item']]
        else:
            items = results['rental_history']['rental_history_item']
        for i in items:
            tags = []
            title = i['title']['regular']
            image_url = i['box_art']['small']
            for link in i['link']:
                if link['title'] == 'web page':
                    link = link['href']
            if hasattr(settings, "NETFLIX_TAGS_FROM_CATEGORIES"):
                categories = []
                if settings.NETFLIX_TAGS_FROM_CATEGORIES:
                    for j in i['category']:
                        if j['scheme'] == 'http://api.netflix.com/categories/genres':
                            categories.append(j['term'])
                    if hasattr(settings, "NETFLIX_TAG_PROCESSOR"):
                        # TODO: error handling if not a function
                        process_tags = settings.NETFLIX_TAG_PROCESSOR
                        tags = tags + process_tags(categories)
                    else:
                        tags = tags + _categories_to_tags(categories)
                        
            timestamp = datetime.fromtimestamp(float(i['returned_date'])) # TODO: use utils.parsedate?
            tags = list(set(tags))
            if hasattr(settings, 'NETFLIX_TAG_ALL'):
                if settings.NETFLIX_TAG_ALL:
                    tags.append(settings.NETFLIX_TAG_ALL)
            _handle_rental(title, link, image_url, tags, timestamp)
    else:
        log.info("No new items. Skipping.")

#
# Private API
#

@transaction.commit_on_success
def _handle_rental(title, link, image_url, tags, timestamp):
    tags = " ".join(tags)
    i, created = Purchase.objects.get_or_create(
        title = title,
        # description = None, # TODO
        url = link,
        image_url = image_url,
    )
    # if not created:
    
    return Item.objects.create_or_update(
        instance = i, 
        timestamp = timestamp, 
        tags = tags,
        source = __name__,
        source_id = _source_id(title, timestamp),
    )

def _categories_to_tags(categories):
    tags = []
    for i in categories:
        tags.append(i.replace(' & ', ' ').replace(' ', '-').lower())
    return tags

def _source_id(title, timestamp):
    return hashlib.md5(smart_str(title) + str(timestamp)).hexdigest()

