import logging
import optparse
import urllib
import oauth2 as oauth
import cgi # parse_qsl is in urlparse in Python2.6
import sys

from django.core.management.base import BaseCommand
from django.conf import settings

REQUEST_TOKEN_URL = 'http://api.netflix.com/oauth/request_token'
ACCESS_TOKEN_URL = 'http://api.netflix.com/oauth/access_token'
AUTHORIZE_URL = 'https://api-user.netflix.com/oauth/login'

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        self.get_request_token()

    def get_request_token(self):
        # Adapted from example usage docs at https://github.com/simplegeo/python-oauth2
        consumer = oauth.Consumer(settings.NETFLIX_CONSUMER_KEY, settings.NETFLIX_CONSUMER_SECRET)
        client = oauth.Client(consumer)
        resp, content = client.request(REQUEST_TOKEN_URL, "GET")
        if resp['status'] != '200':
            print 'Error:', resp['status'], content
            sys.exit()
        request_token = dict(cgi.parse_qsl(content))

        authorize_url_dict = {
            'oauth_token': request_token['oauth_token'],
            'oauth_consumer_key': settings.NETFLIX_CONSUMER_KEY,
            'application_name': settings.NETFLIX_APP_NAME
        }
        # oauth_callback unnecessary in this case

        print "Request Token:"
        print "    - oauth_token        = %s" % request_token['oauth_token']
        print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']

        print "Go to the following link in your browser:"
        print "%s?%s" % (AUTHORIZE_URL, urllib.urlencode(authorize_url_dict))
        print

        accepted = 'n'
        while accepted.lower() == 'n':
            accepted = raw_input('Have you authorized me? (y/n) ')
    
        self.get_access_token(consumer, request_token)
    
    def get_access_token(self, consumer, request_token):
        token = oauth.Token(request_token['oauth_token'],
            request_token['oauth_token_secret'])
        # token.set_verifier(oauth_verifier)
        client = oauth.Client(consumer, token)

        resp, content = client.request(ACCESS_TOKEN_URL, "POST")
        access_token = dict(cgi.parse_qsl(content))    

        print "Access Token:"
        print "    - oauth_token        = %s" % access_token['oauth_token']
        print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
        print
        print "You may now access protected resources using the access tokens above."     
        print "Assign the oauth_token value to NETFLIX_OAUTH_TOKEN and oauth_token_secret"
        print "to NETFLIX_OAUTH_TOKEN_SECRET in your application's settings.py"

