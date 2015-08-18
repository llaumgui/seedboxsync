#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

"""
Seedboxsync, setuptools based setup module.
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from pip.req import parse_requirements
from pip.download import PipSession

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_requirements = parse_requirements('requirements.txt', session=PipSession())
requirements = [str(ir.req) for ir in install_requirements]

setup(
    name='seedboxsync',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.6.0',

    description='Script for sync operations between your NAS and your seedbox',
    url='https://github.com/llaumgui/seedboxsync',

    # Author details
    author='Guillaume Kulakowski',
    author_email='guillaume@kulakowski.fr',

    # Choose your license
    license='GPLv2',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Topic :: Internet',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='seedbox sync sftp',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=requirements,

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'seedboxsync=seedboxsync.seedboxsync:CLI',
        ],
    },
)
