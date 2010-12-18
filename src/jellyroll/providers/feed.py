import hashlib
import datetime
import logging
import dateutil
import re

from django.conf import settings
from django.db import transaction
from django.template.defaultfilters import slugify
from django.utils.functional import memoize
from django.utils.http import urlquote
from django.utils.encoding import smart_str, smart_unicode
from httplib2 import HttpLib2Error
from jellyroll.providers import utils
from jellyroll.models import Item, Feed, FeedEntry

import feedparser

#
# Public API
#

log = logging.getLogger("jellyroll.providers.feed")

def enabled():
    return True

def update():
    for feed in Feed.objects.all():
        _update_posts(feed)

#
# Private API
#
class FeedAPI(object):
    
    def __init__(self, provider_name, tags=[]):
        self.provider = provider_name
        self.tags = tags
    
    def _update_posts(self, feed):

        source_identifier = "%s:%s" % (self.provider, feed.url)
        last_update_date = Item.objects.get_last_update_of_model(FeedEntry, source=source_identifier)
        log.info("Updating changes from %s since %s", feed.url, last_update_date)
    
        d = feedparser.parse(feed.url)
        for i in d['entries']:
            text = ''
            title = i['title']
            if i.has_key('summary'):
                description = i['summary']
                if i.has_key('content'):              
                    text = i['content'][0]['value']
            elif i.has_key('content'):        
                description = i['content'][0]['value'] # either <summary> or <content>
            url = i['link']
            try:
                timestamp = dateutil.parser.parse(i['published']) # TODO: how to handle updates?
            except:
                timestamp = dateutil.parser.parse(i['date'])
            try:
                id = i['id']
            except:
                id = self._source_id(title, url, timestamp)
            if utils.JELLYROLL_ADJUST_DATETIME:
                timestamp = utils.utc_to_local_datetime(timestamp)
            tags = list(self.tags)
            try:
                categories = i['categories']
            except:
                categories = None
            if categories:
                for j in categories:
                    tags.append(j[1])
            if tags:
                tags = ' '.join(c.replace(' ', '-').lower() for c in tags if c not in settings.FEED_EXCLUDE_TAGS)
            else:
                tags = ''
            if not self._post_exists(id):
                self._handle_post(id, feed, title, description, text, url, timestamp, tags)
            else:
                log.debug("%s exists, skipping" % id)

    @transaction.commit_on_success
    def _handle_post(self, id, feed, title, description, text, url, timestamp, tags=''):

        t = FeedEntry(
            feed = feed,
            title = title,
            description = description,
            text = text,
            url = url,
            )

        log.debug("Saving entry: %r", title)
        item = Item.objects.create_or_update(
            instance = t,
            timestamp = timestamp,
            source = self.provider,
            source_id = id,
            url = url,
            tags = tags
            )
        item.save()

    def _post_exists(self, id):
        try:
            Item.objects.get(source=self.provider, source_id=id)
        except Item.DoesNotExist:
            return False
        else:
            return True

    def _source_id(self, title, url, timestamp):
        return hashlib.md5(smart_str(title) + smart_str(url) + str(timestamp)).hexdigest()
