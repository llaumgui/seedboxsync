# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2018 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

"""
Exception module with customs exceptions classes.
"""


class ConnectionException(Exception):
    pass


class ConfigurationException(Exception):
    pass


class DependencyException(Exception):
    pass


class IsLockedException(Exception):
        pass


class LockException(Exception):
    pass


class LogException(Exception):
    pass


class TransportProtocoleException(Exception):
    pass
