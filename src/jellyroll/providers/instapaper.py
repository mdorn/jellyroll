import logging
from jellyroll.models import Item, Feed, FeedEntry
from jellyroll.providers.feed import FeedAPI

#
# Public API
#

log = logging.getLogger("jellyroll.providers.instapaper")

def enabled():
    return True

def update():
    feed = Feed.objects.get(title="Instapaper")
    api = FeedAPI(__name__, tags=['reading'])
    api._update_posts(feed)

