import logging
from jellyroll.models import Item, Feed, FeedEntry
from jellyroll.providers.feed import FeedAPI

#
# Public API
#

log = logging.getLogger("jellyroll.providers.mattdorn_dot_com")

def enabled():
    return True

def update():
    # for feed in Feed.objects.filter(type="atom"):
    feed = Feed.objects.get(title="mattdorn.com")
    api = FeedAPI(__name__)
    api._update_posts(feed)

