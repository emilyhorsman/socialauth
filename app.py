# This is a usage example with Flask.
#
# For details and documentation, check out:
# https://socialauth.readthedocs.org/

import os

import dotenv
import jwt
from flask import (
    Flask, request, current_app, redirect,
    jsonify, make_response, abort
)

import socialauth


app = Flask(__name__)


@app.route('/whoami')
def whoami():
    # User IDs are likely protected values, so exposing this value wouldn't
    # be typically recommended in production.
    res = jwt.decode(request.cookies.get('jwt'), current_app.secret_key)
    return res.get('user_id')


# GET /auth/facebook?login=start
# GET /auth/twitter?login=start
@app.route('/auth/<provider>')
def authenticate(provider):
    res = socialauth.http_get_provider(
        provider,
        request.base_url,          # Callback URL
        request.args,              # GET parameters/query string
        current_app.secret_key,
        request.cookies.get('jwt') # Currently stored token
    )

    if res.get('status') == 302:
        resp = make_response(redirect(res.get('redirect')))
        if res.get('set_token_cookie') is not None:
            resp.set_cookie('jwt', res.get('set_token_cookie'), httponly = True)

        return resp

    if res.get('status') == 200:
        resp = make_response(jsonify({ 'status': 'success' }))
        resp.set_cookie('jwt', res.get('set_token_cookie'), httponly = True)
        return resp

    # Something has gone very wrong. This should not happen.
    abort(400)


if __name__ == '__main__':
    dotenv.load_dotenv('.env')
    app.secret_key = os.urandom(24)
    app.debug = True
    app.run(host = '0.0.0.0')
