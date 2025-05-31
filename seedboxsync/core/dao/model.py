# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

from peewee import Model, Proxy

global_database_object = Proxy()


class SeedboxSyncModel(Model):
    """
    Basemodel from which all other peewee models are derived.
    """

    class Meta:
        database = global_database_object
