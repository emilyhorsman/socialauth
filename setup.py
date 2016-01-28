from setuptools import setup
from os import path


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()


setup(
    name    = 'socialauth',
    version = '0.1.0',

    packages = ['socialauth'],

    description = 'A framework- and backend-independent social login provider.',
    long_description = long_description,

    url = 'https://github.com/emilyhorsman/socialauth',

    author       = 'Emily Horsman',
    author_email = 'me@emilyhorsman.com',

    license = 'MIT',

    classifiers = [
        'Development Status :: 4 - Beta',

        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
