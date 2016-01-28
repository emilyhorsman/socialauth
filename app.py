import os

from flask import (
    Flask, request, current_app, redirect,
    jsonify, make_response, abort
)

import socialauth
import jwt
import dotenv
dotenv.load_dotenv('.env')

app = Flask(__name__)

@app.route('/whoami')
def whoami():
    # User IDs are likely protected values, so exposing this value wouldn't
    # be typically recommended in production.
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


app.secret_key = os.urandom(24)
app.debug = True
app.run(host='0.0.0.0')
