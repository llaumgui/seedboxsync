# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from .blackhole import blackhole, LOCK_NAME as BLACKHONE_LOCK_NAME

__all__ = ["BLACKHONE_LOCK_NAME", "blackhole"]
