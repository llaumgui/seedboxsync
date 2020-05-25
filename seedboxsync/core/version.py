# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2020 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

from cement.utils.version import get_version as cement_get_version

VERSION = (3, 0, 0, 'beta', 1)


def get_version(version=VERSION):
    return cement_get_version(version)
