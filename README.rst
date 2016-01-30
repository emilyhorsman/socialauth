Python Social Auth
==================

.. image:: https://travis-ci.org/emilyhorsman/socialauth.svg?branch=master
    :target: https://travis-ci.org/emilyhorsman/socialauth
    :alt: Travis CI

.. image:: https://coveralls.io/repos/github/emilyhorsman/socialauth/badge.svg?branch=master
    :target: https://coveralls.io/github/emilyhorsman/socialauth?branch=master
    :alt: Coveralls Test Coverage

.. image:: https://readthedocs.org/projects/socialauth/badge/?version=latest
    :target: http://socialauth.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://codeclimate.com/github/emilyhorsman/socialauth/badges/gpa.svg
    :target: https://codeclimate.com/github/emilyhorsman/socialauth
    :alt: Code Climate

.. image:: https://img.shields.io/pypi/v/socialauth.svg
    :target: https://pypi.python.org/pypi/socialauth
    :alt: PyPI

.. image:: https://img.shields.io/badge/python-%E2%89%A5%203.3-blue.svg
    :target: https://docs.python.org/3/
    :alt: Python >= 3.3

.. image:: https://img.shields.io/badge/code%20of%20conduct-v1.4.0-4C1161.svg
    :target: CODE_OF_CONDUCT.md
    :alt: Contributor Covenant Code of Conduct

.. image:: https://img.shields.io/pypi/l/socialauth.svg
    :alt: MIT License


A library for social sign-in capability from providers such as Twitter and
Facebook.

Many social authentication solutions exist. I wanted something that didn’t
have strong ties to an HTTP framework or storage backend. Preferably, I
didn’t want something that dealt with a storage backend at all. This library
uses JSON web tokens instead of sessions to deal with intermediate information
in the OAuth flow (such as a token secret).

.. code-block:: bash

    $ pip install socialauth



Run Tests
=========

.. code-block:: bash

    $ git clone https://github.com/emilyhorsman/socialauth.git
    $ mkvirtualenv --python=python3 socialauth
    $ cd socialauth
    $ workon .
    $ pip install -r requirements.test.txt
    $ python tests.py

Build Docs
==========

.. code-block:: bash

    $ pip install -r requirements.docs.txt
    $ cd docs
    $ make html

