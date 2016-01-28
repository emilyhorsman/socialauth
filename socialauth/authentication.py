import jwt

import socialauth.providers
from . import InvalidUsage

def validate_provider(provider):
    return provider in (
        'twitter',
        'facebook',
    )


def http_get_provider(provider,
                      request_url, params, token_secret, token_cookie = None):
    if not validate_provider(provider):
        raise InvalidUsage('Provider not supported')

    klass    = getattr(socialauth.providers, provider.capitalize())
    provider = klass(request_url, params, token_secret, token_cookie)
    if provider.status == 302:
        ret = dict(status = 302, redirect = provider.redirect)
        tc  = getattr(provider, 'set_token_cookie', None)
        if tc is not None:
            ret['set_token_cookie'] = tc

        return ret

    if provider.status == 200 and provider.user_id is not None:
        payload = dict(user_id = provider.user_id)
        token   = jwt.encode(payload, token_secret, algorithm = 'HS256')
        ret     = dict(status = 200, set_token_cookie = token)
        if provider.user_name is not None:
            ret['user_name'] = provider.user_name

        return ret

    raise InvalidUsage('Invalid request') # pragma: no cover
