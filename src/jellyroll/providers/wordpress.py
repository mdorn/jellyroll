"""
Provider for data from a WordPress blog, including tags
NOTE: tested only with WordPress 2.9
"""
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

#
# API URLs
#

FEED_URL = "%sfeed/"
# TODO: BLOG_COMMENT_FEED_URL = "%scomments/feed/"

#
# Public API
#

log = logging.getLogger("jellyroll.providers.wordpress")

def enabled():
    return True

def update():
    for feed in Feed.objects.filter(type="wordpress"):
        _update_posts(feed)

#
# Private API
#

def _update_posts(feed):

    source_identifier = "%s:%s" % (__name__, feed.url)
    last_update_date = Item.objects.get_last_update_of_model(FeedEntry, source=source_identifier)
    log.info("Updating changes from %s since %s", feed.url, last_update_date)
    
    xml = utils.getxml(FEED_URL % feed.url)
    for i in xml.getiterator('item'):
        title      = smart_unicode(i.find('title').text)
        description = smart_unicode(i.find('description').text)
        url          = smart_unicode(i.find('link').text)
        # pubDate delivered as UTC
        timestamp    = dateutil.parser.parse(i.find('pubDate').text)
        if utils.JELLYROLL_ADJUST_DATETIME:
            timestamp = utils.utc_to_local_datetime(timestamp)
        tags = ' '.join(c.text.replace(' ', '-').lower() for c in i.findall('category') if c.text not in settings.WORDPRESS_EXCLUDE_TAGS)
        if not _post_exists(title, url, timestamp):
            _handle_post(feed, title, description, url, timestamp, tags)

@transaction.commit_on_success
def _handle_post(feed, title, description, url, timestamp, tags):

    t = FeedEntry(
        feed = feed,
        title = title,
        description = description,
        url = url,
        )
    
    if len(tags) < 1:
        tags = ''

    log.debug("Saving entry: %r", title)
    item = Item.objects.create_or_update(
        instance = t,
        timestamp = timestamp,
        source = __name__,
        source_id = _source_id(title, url, timestamp),
        url = url,
        tags = tags,
        )
    item.save()

def _source_id(title, url, timestamp):
    return hashlib.md5(smart_str(title) + smart_str(url) + str(timestamp)).hexdigest()
    
def _post_exists(title, url, timestamp):
    id = _source_id(title, url, timestamp)
    try:
        Item.objects.get(source=__name__, source_id=id)
    except Item.DoesNotExist:
        return False
    else:
        return True
