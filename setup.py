#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

from setuptools import setup, find_packages
from seedboxsync.version import get_version

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='seedboxsync',
    version=get_version(),
    python_requires='>=3.9',
    description='Script for sync operations between your NAS and your seedbox',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Guillaume Kulakowski',
    author_email='guillaume@kulakowski.fr',
    url='https://llaumgui.github.io/seedboxsync/',
    license='GPL-2.0',

    project_urls={
        'Documentation': 'https://llaumgui.github.io/seedboxsync/',
        'Bug Reports': 'https://github.com/llaumgui/seedboxsync/issues',
        'Source': 'https://github.com/llaumgui/seedboxsync/'
    },

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'Topic :: Internet',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 3',
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: POSIX'
    ],
    keywords='seedbox nas sync sftp',

    packages=find_packages(exclude=['ez_setup', 'tests*']),
    data_files=[('config', ['config/seedboxsync.yml.example'])],
    include_package_data=True,
    entry_points="""
        [console_scripts]
        seedboxsync = seedboxsync.main:main
    """,

    install_requires=[
        'cement==3.0.14',
        'pyyaml',
        'colorlog',
        'paramiko>=2.12',
        'bcoding',
        'tabulate',
        'peewee'
    ],
)
