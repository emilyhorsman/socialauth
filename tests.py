# -*- coding: utf-8 -*-

import os
import unittest
from unittest.mock import patch
from urllib.parse import urlparse, parse_qs
from contextlib import contextmanager

import jwt
import httplib2
import socialauth


twitter_base_url  = 'https://test.socialauth.foo/auth/twitter'
facebook_base_url = 'https://test.socialauth.foo/auth/facebook'


def mock_request_with(path, status, body = b''):
    def func(self, uri, *args, **kwargs):
        url = urlparse(uri)
        if url[2].endswith(path):
            return (httplib2.Response(dict(status = status)), body)

        return mock_valid_requests(self, uri, *args, **kwargs)

    return func


def mock_valid_requests(self, uri, *args, **kwargs):
    url = urlparse(uri)

    # https://dev.twitter.com/oauth/reference/post/oauth/request_token
    if url[1] == 'api.twitter.com' and url[2] == '/oauth/request_token':
        res = httplib2.Response(dict(status = 200))
        content = b'oauth_token=foo&oauth_token_secret=bar&oauth_callback_confirmed=true'

    # https://dev.twitter.com/oauth/reference/post/oauth/access_token
    if url[1] == 'api.twitter.com' and url[2] == '/oauth/access_token':
        res = httplib2.Response(dict(status = 200))
        content = b'oauth_token=foo&oauth_token_secret=bar&user_id=987&screen_name=test'

    # https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow#confirm
    if url[1] == 'graph.facebook.com' and url[2].endswith('/oauth/access_token'):
        res = httplib2.Response(dict(status = 200))
        content = b'{"access_token":"foobar","token_type":"bearer","expires_in":5117097}'

    # https://developers.facebook.com/docs/graph-api/using-graph-api
    if url[1] == 'graph.facebook.com' and url[2] == '/me':
        res = httplib2.Response(dict(status = 200))
        content = b'{"id":"987","name":"test"}'

    return (res, content)


@contextmanager
def no_env(key):
    value = os.environ.get(key, '')
    os.environ[key] = ''
    yield
    os.environ[key] = value


class TestHTTPGetProvider(unittest.TestCase):
    def test_invalid_provider(self):
        with self.assertRaises(socialauth.InvalidUsage):
            socialauth.http_get_provider('foobar!', '', {}, '')


class TestTwitterProvider(unittest.TestCase):
    def test_no_env(self):
        with no_env('TWITTER_CONSUMER_KEY'):
            with self.assertRaisesRegex(socialauth.Error,
                                        'No TWITTER_CONSUMER_KEY'):
                socialauth.providers.Twitter('', {}, '', '')

        with no_env('TWITTER_CONSUMER_SECRET'):
            with self.assertRaisesRegex(socialauth.Error,
                                        'No TWITTER_CONSUMER_SECRET'):
                socialauth.providers.Twitter('', {}, '', '')

    def test_no_login_start(self):
        with self.assertRaises(socialauth.InvalidUsage):
            socialauth.providers.Twitter('', {}, '', '')

    def get_provider(self, args, token = None):
        return socialauth.http_get_provider(
            'twitter',
            twitter_base_url,
            args,
            'sekret',
            token
        )

    @patch('httplib2.Http.request', mock_valid_requests)
    def test_no_oauth_token_or_verifier(self):
        args = { 'oauth_token': 'Z6eEdO8MOmk394WozF5oKyuAv855l4Mlqo7hhlSLik' }
        with self.assertRaises(socialauth.InvalidUsage):
            self.get_provider(args, 'foobar')

    @patch('httplib2.Http.request', mock_valid_requests)
    def test_no_token_cookie_given(self):
        args = { 'oauth_token': 'foo', 'oauth_verifier': 'foo' }
        with self.assertRaisesRegex(socialauth.Error, 'No token cookie'):
            self.get_provider(args, '')  # Deliberately blank token cookie

    @patch('httplib2.Http.request', mock_valid_requests)
    def test_no_secret_in_web_token(self):
        args  = { 'oauth_token': 'foo', 'oauth_verifier': 'foo' }
        token = jwt.encode({ 'data': { 'type': 'foobar' } }, 'sekret').decode('utf-8')
        with self.assertRaisesRegex(socialauth.Error, 'does not have an oauth_token_secret'):
            self.get_provider(args, token)

    @patch('httplib2.Http.request', mock_valid_requests)
    def test_invalid_web_token(self):
        args  = { 'oauth_token': 'foo', 'oauth_verifier': 'foo' }
        token = jwt.encode({ 'data': { 'type': 'foobar' } }, 'invalid secret').decode('utf-8')
        with self.assertRaisesRegex(socialauth.Error, 'Failed to retrieve'):
            self.get_provider(args, token)

    @patch('httplib2.Http.request', mock_request_with('access_token', 400))
    def test_no_access_token_from_twitter(self):
        args  = { 'oauth_token': 'foo', 'oauth_verifier': 'foo' }
        token = jwt.encode({ 'data': { 'type': 'oauth_token_secret', 'id': 'foo' } }, 'sekret')
        with self.assertRaisesRegex(socialauth.Error, '400 from Twitter'):
            self.get_provider(args, token)

    @patch(
        'httplib2.Http.request',
        mock_request_with(
            'access_token',
            200,
            b'oauth_token=foo&oauth_token_secret=foo&screen_name=test'
        )
    )
    def test_no_user_id_from_twitter(self):
        args  = { 'oauth_token': 'foo', 'oauth_verifier': 'foo' }
        token = jwt.encode({ 'data': { 'type': 'oauth_token_secret', 'id': 'foo' } }, 'sekret')
        with self.assertRaisesRegex(socialauth.Error, 'No user_id'):
            self.get_provider(args, token)

    @patch('httplib2.Http.request', mock_request_with('request_token', 400, ''))
    def test_request_token_failure(self):
        with self.assertRaisesRegex(socialauth.Error, '400 from Twitter'):
            self.get_provider({ 'login': 'start' })

    @patch('httplib2.Http.request', mock_request_with('request_token', 200, b''))
    def test_blank_request_token(self):
        with self.assertRaisesRegex(socialauth.Error, 'No oauth_token'):
            self.get_provider({ 'login': 'start' })

    @patch('httplib2.Http.request', mock_valid_requests)
    def test_flow(self):
        # First leg
        res = self.get_provider({ 'login': 'start' })
        self.assertEqual(res['status'], 302)
        self.assertIn('/oauth/authenticate?oauth_token', res.get('redirect'))

        payload = jwt.decode(res['set_token_cookie'], 'sekret', algorithm = 'HS256')
        self.assertEqual(payload['data']['type'], 'oauth_token_secret')

        # Second leg
        args = {
            'oauth_token': 'Z6eEdO8MOmk394WozF5oKyuAv855l4Mlqo7hhlSLik',
            'oauth_verifier': 'zvq3SztKJphiXzEbUrzt3E7n8WmhZVsx'
        }

        res = self.get_provider(args, res['set_token_cookie'])

        self.assertEqual(res['status'], 200)
        self.assertEqual(res['provider_user_id'], '987')
        self.assertEqual(res['provider_user_name'], 'test')


class TestFacebookProvider(unittest.TestCase):
    def test_no_env(self):
        with no_env('FACEBOOK_APP_ID'):
            with self.assertRaisesRegex(socialauth.Error,
                                        'No FACEBOOK_APP_ID'):
                socialauth.providers.Facebook('', {}, '', '')

        with no_env('FACEBOOK_APP_SECRET'):
            with self.assertRaisesRegex(socialauth.Error,
                                        'No FACEBOOK_APP_SECRET'):
                socialauth.providers.Facebook('', {}, '', '')

    def test_no_login_start(self):
        with self.assertRaises(socialauth.InvalidUsage):
            socialauth.providers.Facebook('', {}, '', '')

    def get_provider(self, args, token = None):
        return socialauth.http_get_provider(
            'facebook',
            facebook_base_url,
            args,
            'sekret',
            None
        )

    @patch('httplib2.Http.request', mock_request_with('access_token', 400))
    def test_failures(self):
        with self.assertRaisesRegex(socialauth.Error, '400 from Facebook'):
            self.get_provider({ 'code': 'foobar' })

    @patch('httplib2.Http.request', mock_request_with('/me', 400))
    def test_graph_me_failure(self):
        with self.assertRaisesRegex(socialauth.Error, '400 from Facebook'):
            self.get_provider({ 'code': 'foobar' })

    @patch(
        'httplib2.Http.request',
        mock_request_with(
            'access_token',
            200,
            b'{"token_type":"bearer","expires_in":5117097}'
        )
    )
    def test_no_access_token_give(self):
        with self.assertRaisesRegex(socialauth.Error, 'No access token'):
            self.get_provider({ 'code': 'foobar' })

    @patch('httplib2.Http.request', mock_request_with('/me', 200, b'{"name":"test"}'))
    def test_graph_me_no_user_id(self):
        with self.assertRaisesRegex(socialauth.Error, 'No user ID'):
            self.get_provider({ 'code': 'foobar' })

    @patch('httplib2.Http.request', mock_valid_requests)
    def test_flow(self):
        res = self.get_provider({ 'login': 'start' })
        self.assertEqual(res['status'], 302)

        # https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow#login
        args = parse_qs(urlparse(res['redirect'])[4])
        self.assertIn('client_id', args)
        self.assertIn('redirect_uri', args)

        res = self.get_provider({ 'code': 'foo' })
        self.assertEqual(res['status'], 200)
        self.assertEqual(res['provider_user_id'], '987')
        self.assertEqual(res['provider_user_name'], 'test')


if __name__ == '__main__':
    os.environ['TWITTER_CONSUMER_KEY']    = 'foobar'
    os.environ['TWITTER_CONSUMER_SECRET'] = 'foobar'
    os.environ['FACEBOOK_APP_ID']         = '1234'
    os.environ['FACEBOOK_APP_SECRET']     = 'foobar'
    unittest.main()
