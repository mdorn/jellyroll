from __future__ import with_statement

import mock
import datetime
import unittest
from django.conf import settings
from django.test import TestCase
from jellyroll.models import Item, Purchase
from jellyroll.providers import netflix, utils

class NetflixClientTests(unittest.TestCase):
    
    def test_client_getattr(self):
        c = netflix.NetflixClient('aaaa', 'bbbb', None)
        self.assertEqual(c.oauth_token, 'aaaa')
        self.assertEqual(c.oauth_token_secret, 'bbbb')
        self.assertEqual(c.updated_min, None)
        
        c2 = c.foo.bar.baz
        self.assertEqual(c2.oauth_token, 'aaaa')
        self.assertEqual(c2.oauth_token_secret, 'bbbb')
        self.assertEqual(c2.method, 'users/%s/foo/bar/baz' % c.oauth_token)
        
    def test_client_call(self):
        mock_getjson = mock.Mock(return_value={})
        with mock.patch_object(utils, 'getjson', mock_getjson) as mocked:
            c = netflix.NetflixClient('aaaa', 'bbbb', None)
            res = c.foo.bar(a=1, b=2)
            self.assert_(mocked.called)

#
# Mock Netflix client
#

FakeClient = mock.Mock()
FakeClient.return_value = FakeClient

FakeClient.rental_history.returned.return_value = {
    'rental_history': {
        'url_template': 'http://api.netflix.com/users/aaaa-/rental_history/returned?{-join|&|start_index|max_results}',
        'rental_history_item': [{
            'category': [{
                'term': 'Returned',
                'scheme': 'http://api.netflix.com/categories/rental_states',
                'label': 'Returned'
            },
            {
                'term': 'NR',
                'scheme': 'http://api.netflix.com/categories/mpaa_ratings',
                'label': 'NR'
            },
            {
                'term': 'Documentary',
                'scheme': 'http://api.netflix.com/categories/genres',
                'label': 'Documentary'
            },
            {
                'term': 'Social & Cultural Documentaries',
                'scheme': 'http://api.netflix.com/categories/genres',
                'label': 'Social & Cultural Documentaries'
            },
            {
                'term': 'Photography',
                'scheme': 'http://api.netflix.com/categories/genres',
                'label': 'Photography'
            },
            {
                'term': 'Art & Design',
                'scheme': 'http://api.netflix.com/categories/genres',
                'label': 'Art & Design'
            }],
            'box_art': {
                'large': 'http://cdn-1.nflximg.com/us/boxshots/large/70059641.jpg',
                'small': 'http://cdn-1.nflximg.com/us/boxshots/tiny/70059641.jpg',
                'medium': 'http://cdn-1.nflximg.com/us/boxshots/small/70059641.jpg'
            },
            'release_year': '2007',
            'title': {
                'regular': 'Manufactured Landscapes',
                'short': 'Manufactured Landscapes'
            },
            'updated': '1288583594',
            'average_rating': '3.6',
            'link': [{
                'href': 'http://api.netflix.com/catalog/titles/movies/70059641',
                'rel': 'http://schemas.netflix.com/catalog/title',
                'title': 'Manufactured Landscapes'
            },
            {
                'href': 'http://api.netflix.com/catalog/titles/movies/70059641/synopsis',
                'rel': 'http://schemas.netflix.com/catalog/titles/synopsis',
                'title': 'synopsis'
            },
            {
                'href': 'http://api.netflix.com/catalog/titles/movies/70059641/cast',
                'rel': 'http://schemas.netflix.com/catalog/people.cast',
                'title': 'cast'
            },
            {
                'href': 'http://api.netflix.com/catalog/titles/movies/70059641/directors',
                'rel': 'http://schemas.netflix.com/catalog/people.directors',
                'title': 'directors'
            },
            {
                'href': 'http://api.netflix.com/catalog/titles/movies/70059641/format_availability',
                'rel': 'http://schemas.netflix.com/catalog/titles/format_availability',
                'title': 'formats'
            },
            {
                'href': 'http://api.netflix.com/catalog/titles/movies/70059641/screen_formats',
                'rel': 'http://schemas.netflix.com/catalog/titles/screen_formats',
                'title': 'screen formats'
            },
            {
                'href': 'http://api.netflix.com/catalog/titles/movies/70059641/languages_and_audio',
                'rel': 'http://schemas.netflix.com/catalog/titles/languages_and_audio',
                'title': 'languages and audio'
            },
            {
                'href': 'http://api.netflix.com/catalog/titles/movies/70059641/similars',
                'rel': 'http://schemas.netflix.com/catalog/titles.similars',
                'title': 'similars'
            },
            {
                'href': 'http://www.netflix.com/Movie/Manufactured_Landscapes/70059641',
                'rel': 'alternate',
                'title': 'web page'
            }],
            'returned_date': '1288583594',
            'runtime': '5400',
            'id': 'http://api.netflix.com/users/aaaa-/rental_history/returned/70059641'
        },
        {
            'category': [{
                'term': 'Returned',
                'scheme': 'http://api.netflix.com/categories/rental_states',
                'label': 'Returned'
            },
            {
                'term': 'PG',
                'scheme': 'http://api.netflix.com/categories/mpaa_ratings',
                'label': 'PG'
            },
            {
                'term': 'Classics',
                'scheme': 'http://api.netflix.com/categories/genres',
                'label': 'Classics'
            },
            {
                'term': 'Classic Thrillers',
                'scheme': 'http://api.netflix.com/categories/genres',
                'label': 'Classic Thrillers'
            },
            {
                'term': 'Espionage Thrillers',
                'scheme': 'http://api.netflix.com/categories/genres',
                'label': 'Espionage Thrillers'
            },
            {
                'term': 'Psychological Thrillers',
                'scheme': 'http://api.netflix.com/categories/genres',
                'label': 'Psychological Thrillers'
            }],
            'box_art': {
                'large': 'http://cdn-9.nflximg.com/us/boxshots/large/70042799.jpg',
                'small': 'http://cdn-9.nflximg.com/us/boxshots/tiny/70042799.jpg',
                'medium': 'http://cdn-9.nflximg.com/us/boxshots/small/70042799.jpg'
            },
            'release_year': '1975',
            'title': {
                'regular': 'The Passenger',
                'short': 'The Passenger'
            },
            'updated': '1287108821',
            'average_rating': '3.2',
            'link': [{
                'href': 'http://api.netflix.com/catalog/titles/movies/70042799',
                'rel': 'http://schemas.netflix.com/catalog/title',
                'title': 'The Passenger'
            },
            {
                'href': 'http://api.netflix.com/catalog/titles/movies/70042799/synopsis',
                'rel': 'http://schemas.netflix.com/catalog/titles/synopsis',
                'title': 'synopsis'
            },
            {
                'href': 'http://api.netflix.com/catalog/titles/movies/70042799/cast',
                'rel': 'http://schemas.netflix.com/catalog/people.cast',
                'title': 'cast'
            },
            {
                'href': 'http://api.netflix.com/catalog/titles/movies/70042799/directors',
                'rel': 'http://schemas.netflix.com/catalog/people.directors',
                'title': 'directors'
            },
            {
                'href': 'http://api.netflix.com/catalog/titles/movies/70042799/format_availability',
                'rel': 'http://schemas.netflix.com/catalog/titles/format_availability',
                'title': 'formats'
            },
            {
                'href': 'http://api.netflix.com/catalog/titles/movies/70042799/screen_formats',
                'rel': 'http://schemas.netflix.com/catalog/titles/screen_formats',
                'title': 'screen formats'
            },
            {
                'href': 'http://api.netflix.com/catalog/titles/movies/70042799/languages_and_audio',
                'rel': 'http://schemas.netflix.com/catalog/titles/languages_and_audio',
                'title': 'languages and audio'
            },
            {
                'href': 'http://api.netflix.com/catalog/titles/movies/70042799/similars',
                'rel': 'http://schemas.netflix.com/catalog/titles.similars',
                'title': 'similars'
            },
            {
                'href': 'http://www.sonyclassics.com/thepassenger/index_content.html',
                'rel': 'http://schemas.netflix.com/catalog/titles/official_url',
                'title': 'official webpage'
            },
            {
                'href': 'http://www.netflix.com/Movie/The_Passenger/70042799',
                'rel': 'alternate',
                'title': 'web page'
            }],
            'returned_date': '1287108821',
            'runtime': '7560',
            'id': 'http://api.netflix.com/users/aaaa-/rental_history/returned/70042799'
        }],
        'results_per_page': '10',
        'start_index': '0',
        'number_of_results': '2'
    }
}

class NetflixProviderTests(TestCase):
    
    def test_enabled(self):
        self.assertEqual(netflix.enabled(), True)
        
    @mock.patch_object(netflix, 'NetflixClient', FakeClient)
    def test_update(self):
        netflix.update()
    
        FakeClient.assert_called_with(settings.NETFLIX_OAUTH_TOKEN, settings.NETFLIX_OAUTH_TOKEN_SECRET, 1)
        FakeClient.rental_history.returned.assert_called_with()
        
        # Check that the returned rental exists
        p = Purchase.objects.get(url="http://www.netflix.com/Movie/The_Passenger/70042799")
        self.assertEqual(p.title, "The Passenger")
        # Check that the Item exists
        i = Item.objects.get(content_type__model='purchase', object_id=p.pk)
        self.assertEqual(i.timestamp.date(), datetime.date(2010, 10, 14))
    

