#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2018 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

"""
Seedboxsync, setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
# Get the version from the VERSION file
with open(path.join(here, 'VERSION'), encoding='utf-8') as f:
    version = f.read().strip()

# Setup part
setup(
    name='seedboxsync',
    version=version,
    description='Script for sync operations between your NAS and your seedbox',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://llaumgui.github.io/seedboxsync',
    author='Guillaume Kulakowski',
    author_email='guillaume@kulakowski.fr',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'Topic :: Internet',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 3',
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: POSIX',
    ],

    keywords='seedbox nas sync sftp',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    # Requirements
    install_requires=[
        'paramiko>=2.2.1',
        'bcoding>=1.5',
        'prettytable>=0.7.2',
    ],
    extras_require={
        'dev': ['tox', 'travis-sphinx', 'sphinx_rtd_theme']
    },

    data_files=[('etc', ['seedboxsync.ini.dist'])],
    entry_points={
        'console_scripts': [
            'seedboxsync=seedboxsync.__main__:entry_point',
        ],
    },

    project_urls={
        'Bug Reports': 'https://github.com/llaumgui/seedboxsync/issues',
        'Source': 'https://github.com/llaumgui/seedboxsync/',
    },
)
