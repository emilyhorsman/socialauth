from setuptools import setup
from os import path


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()


setup(
    name    = 'socialauth',
    version = '0.2.0',

    packages = [
        'socialauth',
        'socialauth.providers',
    ],

    description = 'A framework- and backend-independent social login provider.',
    long_description = long_description,

    url = 'https://github.com/emilyhorsman/socialauth',

    author       = 'Emily Horsman',
    author_email = 'me@emilyhorsman.com',

    license = 'MIT',

    install_requires = [
        'httplib2>=0.9.2',
        'oauth2>=1.9.0.post1',
        'PyJWT>=1.4.0'
    ],

    classifiers = [
        'Development Status :: 4 - Beta',

        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
