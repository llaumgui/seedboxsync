#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

"""
Start CLI interface.
"""

from seedboxsync import CLI
import os
import sys

# If avalaible, insert local directories into path
if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seedboxsync')):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    cli = CLI()
