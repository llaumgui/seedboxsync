# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2018 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

"""
SeedboxSync entry point.

Exit code:
    - 0: All is good
    - 1:
    - 2: Logging error
    - 3: Lock error
    - 4: Transfert error
    - 5: Configuration error
    - 6: Unsupported protocole
    - 8: Dependency error
"""

# If avalaible, insert local directories into path
try:
    from seedboxsync.exceptions import (ConnectionException, ConfigurationException, DependencyException,
                                        IsLockedException, LockException, LogException, TransportProtocoleException)
    from seedboxsync.cli import CLI
    from seedboxsync.helper import Helper
except DependencyException as exc:
    print(str(exc))
    exit(8)


def entry_point():
    """
    Entry point
    """
    try:
        CLI()
    except LogException as exc:
        exit(2)
        print(str(exc))
    except LockException as exc:
        exit(2)
        print(str(exc))
    except ConnectionException as exc:
        Helper.log_print(str(exc), msg_type='error')
        exit(4)
    except ConfigurationException as exc:
        Helper.log_print(str(exc), msg_type='error')
        exit(5)
    except TransportProtocoleException as exc:
        print(str(exc))
        exit(6)
    except DependencyException as exc:
        print(str(exc))
        exit(8)
    except IsLockedException:
        exit(0)
    except KeyboardInterrupt:
        exit(0)
