# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from flask import Blueprint
from flask_restx import Api
from seedboxsync.__version__ import (
    __api_version__ as api_version,
    __api_path_version__ as api_path_version,
)
from seedboxsync.front.apis.resources import DateTimeOrZero, Resource
from seedboxsync.front.apis.downloads import api as nsDownloads
from seedboxsync.front.apis.locks import api as nsLocks
from seedboxsync.front.apis.uploads import api as nsUploads

bp = Blueprint("api", __name__, url_prefix=f"/api/{api_path_version}")


api = Api(
    bp,
    title="SeedboxSync API",
    version=api_version,
    description="REST API providing access to the SeedboxSync database and its resources.",
    validate=True,
)

# Add namespaces
api.add_namespace(nsDownloads)
api.add_namespace(nsLocks)
api.add_namespace(nsUploads)

__all__ = ["DateTimeOrZero", "Resource"]
