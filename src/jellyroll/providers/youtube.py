import datetime
import logging
import feedparser
from django.conf import settings
from django.db import transaction
from django.utils.encoding import smart_unicode, smart_str
from django.utils.encoding import DjangoUnicodeDecodeError
from jellyroll.models import Item, VideoSource, Video
from jellyroll.providers import utils

TAG_SCHEME = 'http://gdata.youtube.com/schemas/2007/keywords.cat'
FEED_URL = 'http://gdata.youtube.com/feeds/api/users/%s/favorites?v=2&start-index=%s&max-results=%s'

log = logging.getLogger("jellyroll.providers.youtube")

#
# Public API
#
def enabled():
    ok = hasattr(settings, "YOUTUBE_USERNAME")
    if not ok:
        log.warn('The Youtube provider is not available because the '
                 'YOUTUBE_USERNAME settings is undefined undefined.')
    return ok

def update():    
    start_index = 1
    max_results = 50
    while True:
        log.debug("Fetching videos %s - %s" % (start_index, start_index+max_results-1))
        feed = feedparser.parse(FEED_URL % (settings.YOUTUBE_USERNAME, start_index, max_results))
        for entry in feed.entries:            
            if 'link' in entry:
                url = entry.link
                video_id = entry.videoid
            elif 'yt_videoid' in entry:
                url = 'http://www.youtube.com/watch?v=%s' % entry.yt_videoid
                video_id = entry.yt_videoid
            else:
                log.error("Video '%s' appears to have no link" % (entry.tite))
                continue
                
            _handle_video(
                title = entry.title, 
                url = url,
                tags = " ".join(t['term'] for t in entry.tags if t['scheme'] == TAG_SCHEME),
                timestamp = datetime.datetime(*entry.published_parsed[:6]),
                source_id = video_id
            )
        if len(feed.entries) < max_results:
            log.debug("Ran out of results; finishing.")
            break
            
        start_index += max_results
#
# Private API
#

@transaction.commit_on_success
def _handle_video(title, url, tags, timestamp, source_id):
    log.debug("Handling video: %s" % smart_str(title))
    source = VideoSource.objects.get(name="YouTube")
    
    # For some strange reason sometimes the YouTube API returns
    # corrupted titles...
    try:
        title = smart_unicode(title)
    except DjangoUnicodeDecodeError:
        return
        
    vid, created = Video.objects.get_or_create(
        url = url, 
        defaults = {
            'title': title, 
            'source': source
        }
    )
    if created:
        return Item.objects.create_or_update(
            instance = vid, 
            timestamp = timestamp,
            tags = tags,
            source = __name__,
            source_id = source_id
        )
