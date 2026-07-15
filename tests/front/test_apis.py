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


def test_404(client):
    response = client.get(f"{API_PATH}/404")
    assert response.status_code == 404
    assert response.json["title"] == "Not Found"


def test_400(client):
    response = client.get(f"{API_PATH}/downloads?limit=_ERROR_")
    assert response.status_code == 400
    assert response.json["title"] == "Input payload validation failed"
    assert "limit" in response.json["message"]
    response = client.get(f"{API_PATH}/downloads?limit=5&finished=_ERROR_")
    assert response.status_code == 400
    assert response.json["title"] == "Input payload validation failed"
    assert "finished" in response.json["message"]


def test_swagger(client):
    response = client.get(f"{API_PATH}/")
    assert response.status_code == 200
    assert b"<title>SeedboxSync API</title>" in response.data  # Is HTML
