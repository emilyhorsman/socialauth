# -*- coding: utf-8 -*-

import os
import unittest
from urllib.parse import urlparse, parse_qs
from contextlib import contextmanager

import socialauth
import jwt
from splinter import Browser


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

    def test_flow(self):
        base_url = 'https://test.socialauth.foo/auth/twitter'
        res = socialauth.http_get_provider(
            'twitter',
            base_url,
            { 'login': 'start' },
            'sekret',
            None
        )

        self.assertEqual(res['status'], 302)
        self.assertIn('redirect', res)
        self.assertIn('set_token_cookie', res)
        payload = jwt.decode(res['set_token_cookie'], 'sekret', algorithm = 'HS256')
        self.assertEqual(payload['data']['type'], 'oauth_token_secret')

        with Browser() as browser:
            browser.visit(res.get('redirect'))
            browser.fill('session[username_or_email]', os.environ.get('TWITTER_TEST_USERNAME'))
            browser.fill('session[password]', os.environ.get('TWITTER_TEST_PASSWORD'))
            browser.find_by_id('allow').click()

            url = urlparse(browser.url)

        args = parse_qs(url[4])
        args = { k: v[0] for k, v in args.items() }
        res = socialauth.http_get_provider(
            'twitter',
            base_url,
            args,
            'sekret',
            res['set_token_cookie']
        )

        self.assertEqual(res['status'], 200)
        payload = jwt.decode(res['set_token_cookie'], 'sekret', algorithm = 'HS256')
        self.assertEqual(payload['user_id'], os.environ.get('TWITTER_TEST_USER_ID'))


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

    def test_flow(self):
        base_url = 'https://test.socialauth.foo/auth/facebook'
        res = socialauth.http_get_provider(
            'facebook',
            base_url,
            { 'login': 'start' },
            'sekret',
            None
        )

        self.assertEqual(res['status'], 302)
        self.assertIn('redirect', res)

        with Browser() as browser:
            browser.visit(res.get('redirect'))
            browser.fill('email', os.environ.get('FACEBOOK_TEST_EMAIL'))
            browser.fill('pass', os.environ.get('FACEBOOK_TEST_PASSWORD'))
            browser.find_by_name('login').click()

            url = urlparse(browser.url)

        args = parse_qs(url[4])
        args = { k: v[0] for k, v in args.items() }
        self.assertIn('code', args)

        res = socialauth.http_get_provider(
            'facebook',
            base_url,
            args,
            'sekret',
            None
        )

        self.assertEqual(res['status'], 200)
        payload = jwt.decode(res['set_token_cookie'], 'sekret', algorithm = 'HS256')
        self.assertEqual(payload['user_id'], os.environ.get('FACEBOOK_TEST_USER_ID'))

    def test_borked_oauth_code(self):
        with self.assertRaisesRegex(socialauth.Error, '400 from Facebook'):
            socialauth.providers.Facebook(
                'https://test.socialauth.foo/auth/facebook',
                { 'code': 'foobar' },
                'sekret',
                None
            )


if __name__ == '__main__':
    import dotenv
    dotenv.load_dotenv('.test.env')
    unittest.main()
