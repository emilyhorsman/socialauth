import os
from urllib.parse import parse_qsl

import oauth2
import jwt

from socialauth import Error
from socialauth import InvalidUsage


class Twitter:
    def __init__(self, request_url, params, token_secret, token_cookie):
        self.request_url  = request_url
        self.params       = params
        self.token_secret = token_secret
        self.token_cookie = token_cookie

        self.status             = False
        self.user_id            = None
        self.user_name          = None

        self.set_token_cookie   = None
        self.oauth_verifier     = params.get('oauth_verifier', None)
        self.oauth_token        = params.get('oauth_token', None)
        self.oauth_token_secret = None

        self.consumer_key = os.environ.get('TWITTER_CONSUMER_KEY', None)
        if not self.consumer_key:
            raise Error('No TWITTER_CONSUMER_KEY environment value')

        self.consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET', None)
        if not self.consumer_secret:
            raise Error('No TWITTER_CONSUMER_SECRET environment value')

        self.consumer = oauth2.Consumer(
            key       = self.consumer_key,
            secret    = self.consumer_secret)

        if params.get('login') == 'start':
            self.start()
        elif self.oauth_verifier and self.oauth_token:
            self.finish()
        else:
            raise InvalidUsage('Invalid request')

    def start(self):
        self.get_initial_oauth_tokens()
        self.get_redirect_with_token()

    def finish(self):
        self.decode_oauth_token_secret()
        self.get_user_information()

    def decode_oauth_token_secret(self):
        if not self.token_cookie:
            raise Error('No token cookie given')

        try:
            payload = jwt.decode(self.token_cookie,
                                 self.token_secret,
                                 algorithm = 'HS256')
        except:
            raise Error('Failed to retrieve oauth_token_secret from token')

        self.oauth_token_secret = payload.get('data', {}).get('id', None)
        if not self.oauth_token_secret:
            raise Error('Token does not have an oauth_token_secret')

        return self.oauth_token_secret

    def get_user_information(self):
        token = oauth2.Token(self.oauth_token, self.oauth_token_secret)
        token.set_verifier(self.oauth_verifier)
        client = oauth2.Client(self.consumer, token)

        url = 'https://api.twitter.com/oauth/access_token'
        resp, content = client.request(url, 'POST')
        if resp.status != 200:
            raise Error('{} from Twitter'.format(resp.status))

        provider_user = dict(parse_qsl(content.decode('utf-8')))
        if 'user_id' not in provider_user:
            raise Error('No user_id from Twitter')

        self.status    = 200
        self.user_id   = provider_user.get('user_id')
        self.user_name = provider_user.get('screen_name', None)
        return (self.user_id, self.user_name,)

    def get_initial_oauth_tokens(self):
        url = 'https://api.twitter.com/oauth/request_token'
        client = oauth2.Client(self.consumer)
        resp, content = client.request(url, 'GET')
        if resp.status != 200:
            raise Error('{} from Twitter'.format(resp.status))

        oauth_values = dict(parse_qsl(content.decode('utf-8')))
        self.oauth_token        = oauth_values.get('oauth_token')
        self.oauth_token_secret = oauth_values.get('oauth_token_secret')
        if not self.oauth_token or not self.oauth_token_secret:
            raise Error('No oauth_token or oauth_token_secret from Twitter')

        return (self.oauth_token, self.oauth_token_secret,)

    def get_redirect_with_token(self):
        url = 'https://api.twitter.com/oauth/authenticate?oauth_token={}'
        url = url.format(self.oauth_token)

        # Formatted by JSON API spec (jsonapi.org)
        payload = { 'data': {
            'type': 'oauth_token_secret',
            'id': self.oauth_token_secret
        } }

        self.set_token_cookie = jwt.encode(payload,
                                           self.token_secret,
                                           algorithm = 'HS256')
        self.status   = 302
        self.redirect = url
        return (self.redirect, self.set_token_cookie,)
