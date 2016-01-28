Python Social Auth
==================

.. image:: https://img.shields.io/pypi/v/socialauth.svg
    :target: https://pypi.python.org/pypi/socialauth

.. image:: https://img.shields.io/badge/python-%E2%89%A5%203.3-blue.svg
    :target: https://docs.python.org/3/

.. image:: https://img.shields.io/badge/code%20of%20conduct-v1.3.0-4C1161.svg
    :target: CODE_OF_CONDUCT.md

.. image:: https://img.shields.io/pypi/l/socialauth.svg


A generic library to authenticate with login providers such as Twitter and Facebook.

.. code-block::

    $ pip install socialauth

Flask Example
=============

.. code-block:: python

    @app.route('/whoami')
    def whoami():
        res = jwt.decode(request.cookies.get('jwt'), current_app.secret_key)
        return res.get('user_id')


    @app.route('/auth/<provider>')
    def authenticate(provider):
        res = socialauth.http_get_provider(
            provider,
            request.base_url,
            request.args,
            current_app.secret_key,
            request.cookies.get('jwt')
        )

        if res.get('status') == 302:
            resp = make_response(redirect(res.get('redirect')))
            if res.get('set_token_cookie') is not None:
                resp.set_cookie('jwt', res.get('set_token_cookie'))

            return resp

        if res.get('status') == 200:
            resp = make_response(jsonify({ 'status': 'success' }))
            resp.set_cookie('jwt', res.get('set_token_cookie'))
            return resp

        abort(400)

Current Providers
=================

* Twitter
* Facebook

Why?
====

Many social authentication solutions exist. I wanted something that didn’t
have strong ties to an HTTP framework or storage backend. Preferably, I
didn’t want something that dealt with a storage backend at all. This library
uses JSON web tokens instead of sessions to deal with intermediate information
in the OAuth flow (such as a token secret).
