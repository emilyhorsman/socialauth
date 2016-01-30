Usage Example
=============

Full Example
------------

socialauth uses JSON web tokens to store intermediate data within the OAuth
flow. This means the client holds on to necessary state — not the server. The
server remains stateless and does not use sessions.

This Flask_ example uses cookies to store the token on the client.

socialauth is designed to handle both the start and completion of the OAuth
flow (user’s initial request, callback from provider) in the same route with
the same :func:`socialauth.http_get_provider` call.


.. literalinclude:: ../app.py
    :language: python
    :emphasize-lines: 31-39,44,52
    :linenos:


.. _Flask: http://flask.pocoo.org/
