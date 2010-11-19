import logging
from jellyroll.models import Item, Feed, FeedEntry
from jellyroll.providers.feed import FeedAPI

#
# Public API
#

log = logging.getLogger("jellyroll.providers.github")

def enabled():
    return True

def update():
    # for feed in Feed.objects.filter(type="atom"):
    feed = Feed.objects.get(title="GitHub")
    api = FeedAPI(__name__, tags=['programming'])
    api._update_posts(feed)

