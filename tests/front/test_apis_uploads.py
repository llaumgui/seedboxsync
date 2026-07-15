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


def test_get_uploads_list(client):
    # Default
    response = client.get(f"{API_PATH}/uploads")
    assert response.status_code == 200
    assert response.json["data"][3]["id"] == 247
    assert response.json["data"][3]["name"] == "SuscipitLigulaIn.torrent"
    assert response.json["data"][3]["sent"] == "2017-10-16T21:13:02.851925"
    assert response.json["data_total"] == 250
    assert len(response.json["data"]) == DEFAULT
    # With param limit
    response = client.get(f"{API_PATH}/uploads?limit=6")
    assert len(response.json["data"]) == 6
    # Out of the limit
    response = client.get(f"{API_PATH}/uploads?limit=1001")
    assert len(response.json["data"]) == 250


def test_get_uploads(client):
    # Default
    response = client.get(f"{API_PATH}/uploads/100")
    assert response.status_code == 200
    assert response.json["data"]["sent"] == "2017-09-10T19:52:03.455537"
    assert response.json["data"]["id"] == 100
    assert response.json["data"]["name"] == "Justo.torrent"


def test_get_uploads_404(client):
    # Default
    response = client.get(f"{API_PATH}/uploads/9999999")
    assert response.status_code == 404
    assert response.json["title"] == "Upload 9999999 doesn't exist"


def test_delete_uploads(client):
    # Default
    response = client.delete(f"{API_PATH}/uploads/102")
    assert response.status_code == 200
    assert response.json["message"] == "Upload 102 deleted."
    response = client.get(f"{API_PATH}/uploads/102")
    assert response.status_code == 404
    assert response.json["title"] == "Upload 102 doesn't exist"


def test_delete_uploads_404(client):
    # Default
    response = client.delete(f"{API_PATH}/uploads/9999999")
    assert response.status_code == 404
    assert response.json["title"] == "Upload 9999999 doesn't exist"
