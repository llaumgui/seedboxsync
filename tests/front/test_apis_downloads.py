#
# Copyright (C) 2025-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from seedboxsync.__version__ import __api_path_version__ as api_path_version

DEFAULT = 50
API_PATH = f"/api/{api_path_version}"


def test_get_downloads_list(client):
    # Default
    response = client.get(f"{API_PATH}/downloads")
    assert response.status_code == 200
    assert response.json["data"][2]["finished"] == "2025-05-20T21:50:46"
    assert response.json["data"][2]["id"] == 997
    assert response.json["data"][2]["local_size"] == 3912090693
    assert response.json["data"][2]["human_local_size"] == "3.6 GiB"
    assert response.json["data"][2]["path"] == "FelisSedLacus.ppt"
    assert response.json["data_total"] == 1000
    assert len(response.json["data"]) == DEFAULT
    # With param limit
    response = client.get(f"{API_PATH}/downloads?limit=6")
    assert response.json["data_total"] == 1000
    assert len(response.json["data"]) == 6
    # Out of the limit
    response = client.get(f"{API_PATH}/downloads?limit=1001")
    assert response.json["data_total"] == 1000
    assert len(response.json["data"]) == 1000


def test_get_downloads_list_progress(client):
    # Default
    response = client.get(f"{API_PATH}/downloads?finished=false")
    assert response.status_code == 200
    assert response.json["data"][1]["finished"] == 0
    assert response.json["data"][1]["id"] == 999
    assert response.json["data"][1]["local_size"] == 1004650709
    assert response.json["data"][1]["human_local_size"] == "958.1 MiB"
    assert response.json["data"][1]["path"] == "ConvallisMorbi.doc"
    assert response.json["data_total"] == 2
    assert len(response.json["data"]) == 2


def test_delete_downloads_progress(client):
    # Default
    response = client.delete(f"{API_PATH}/downloads/progress")
    assert response.status_code == 200
    assert response.json["message"] == "2 download(s) deleted."
    response = client.get(f"{API_PATH}/downloads?finished=false")
    assert response.status_code == 200
    assert len(response.json["data"]) == 0


def test_get_downloads(client):
    # Default
    response = client.get(f"{API_PATH}/downloads/1000")
    assert response.status_code == 200
    assert response.json["data"]["finished"] == "2025-05-30T01:47:04"
    assert response.json["data"]["id"] == 1000
    assert response.json["data"]["local_size"] == 3529149958
    assert response.json["data"]["human_local_size"] == "3.3 GiB"
    assert response.json["data"]["path"] == "Quis.mpeg"


def test_get_downloads_404(client):
    # Default
    response = client.get(f"{API_PATH}/downloads/9999999")
    assert response.status_code == 404
    assert response.json["title"] == "Download 9999999 doesn't exist"


def test_delete_downloads(client):
    # Default
    response = client.delete(f"{API_PATH}/downloads/1000")
    assert response.status_code == 200
    assert response.json["message"] == "Download 1000 deleted."
    response = client.get(f"{API_PATH}/downloads/1000")
    assert response.status_code == 404
    assert response.json["title"] == "Download 1000 doesn't exist"


def test_delete_downloads_404(client):
    # Default
    response = client.delete(f"{API_PATH}/downloads/9999999")
    assert response.status_code == 404
    assert response.json["title"] == "Download 9999999 doesn't exist"


def test_get_downloads_stats_month(client):
    response = client.get(f"{API_PATH}/downloads/stats/month")
    assert response.status_code == 200
    assert response.json["data"][89]["files"] == 14
    assert response.json["data"][89]["month"] == "2025-02"
    assert response.json["data"][89]["total_size"] == "37.1GiB"
    assert len(response.json["data"]) == 93


def test_get_downloads_stats_year(client):
    response = client.get(f"{API_PATH}/downloads/stats/year")
    assert response.status_code == 200
    assert response.json["data"][4]["files"] == 143
    assert response.json["data"][4]["total_size"] == "308.3GiB"
    assert response.json["data"][4]["year"] == "2021"
    assert len(response.json["data"]) == 9
