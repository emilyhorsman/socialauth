import os
import json
from urllib.parse import quote

import httplib2
import jwt
from socialauth import Error
from socialauth import InvalidUsage


class Facebook:
    def __init__(self, request_url, params, token_secret, token_cookie):
        self.request_url  = request_url
        self.params       = params
        self.token_cookie = token_cookie
        self.token_secret = token_secret

        self.status       = False
        self.access_token = None
        self.user_id      = None
        self.user_name    = None

        self.client_id = os.environ.get('FACEBOOK_APP_ID', None)
        if not self.client_id:
            raise Error('No FACEBOOK_APP_ID environment value')

        self.client_secret = os.environ.get('FACEBOOK_APP_SECRET', None)
        if not self.client_secret:
            raise Error('No FACEBOOK_APP_SECRET environment value')

        self.api_version = os.environ.get('FACEBOOK_GRAPH_API_VERSION', 'v2.5')

        if params.get('login') == 'start':
            self.start()
        elif 'code' in params:
            self.finish()
        else:
            raise InvalidUsage('Invalid request')

    def start(self):
        url = 'https://www.facebook.com/dialog/oauth?client_id={}&redirect_uri={}'
        url = url.format(self.client_id, quote(self.request_url))
        self.status = 302
        self.redirect = url

    def finish(self):
        self.get_access_token()
        self.get_user_information()

        if self.user_id is not None:
            self.status = 200

    def get_access_token(self):
        qs = 'client_id={}&redirect_uri={}&client_secret={}&code={}'
        qs = qs.format(
            self.client_id,
            quote(self.request_url),
            self.client_secret,
            self.params.get('code'))

        url = 'https://graph.facebook.com/{}/oauth/access_token?{}'
        url = url.format(self.api_version, qs)

        resp, content = httplib2.Http().request(url, 'GET')
        if resp.status != 200:
            raise Error('{} from Facebook'.format(resp.status))

        res = json.loads(content.decode('utf-8'))
        access_token = res.get('access_token', None)
        if access_token is None:
            raise Error('No access token from Facebook')

        self.access_token = access_token
        return access_token

    def get_user_information(self):
        url = 'https://graph.facebook.com/me?fields=id,name&access_token={}'
        url = url.format(self.access_token, self.access_token)

        resp, content = httplib2.Http().request(url, 'GET')
        if resp.status != 200:
            raise Error('{} from Facebook'.format(resp.status))

        res = json.loads(content.decode('utf-8'))
        self.user_id = res.get('id', None)
        if not self.user_id:
            raise Error('No user ID from Facebook')

        self.user_name = res.get('name', None)
        return (self.user_id, self.user_name)
