# -*- coding: utf-8 -*-
#
# Copyright (C) 2025-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from seedboxsync.__version__ import __api_path_version__ as api_path_version

DEFAULT = 50
API_PATH = f"/api/{api_path_version}"


def test_get_locks_list(client):
    # Default
    response = client.get(f"{API_PATH}/locks")
    assert response.status_code == 200
    assert response.json["data"][0]["key"] == "sync_blackhole"
    assert response.json["data"][0]["pid"] == 0
    assert response.json["data"][0]["locked"] is False
    assert response.json["data"][0]["locked_at"] == "2025-10-13T15:37:46.747181"
    assert response.json["data"][0]["unlocked_at"] == "2025-10-13T15:37:46.752033"
    assert len(response.json["data"]) == 2


def test_get_locks(client):
    # Default
    response = client.get(f"{API_PATH}/locks/sync_seedbox")
    assert response.status_code == 200
    assert response.json["data"]["key"] == "sync_seedbox"
    assert response.json["data"]["pid"] == 84074
    assert response.json["data"]["locked"] is True
    assert response.json["data"]["locked_at"] == "2025-10-13T15:38:29.652233"
    assert response.json["data"]["unlocked_at"] is None


def test_get_locks_404(client):
    # Default
    response = client.get(f"{API_PATH}/locks/test")
    assert response.status_code == 404
    assert response.json["title"] == "Lock test doesn't exist"
