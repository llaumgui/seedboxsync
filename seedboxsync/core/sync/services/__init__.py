#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from .blackhole import LOCK_NAME as BLACKHOLE_LOCK_NAME, blackhole
from .seedbox import LOCK_NAME as SEEDBOX_LOCK_NAME, seedbox

__all__ = ["BLACKHOLE_LOCK_NAME", "SEEDBOX_LOCK_NAME", "blackhole", "seedbox"]
