#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Peewee model."""
from peewee import Model


class SeedboxSyncModel(Model):
    """Basemodel from which all other peewee models are derived."""
