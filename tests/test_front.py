# -*- coding: utf-8 -*-
#
# Copyright (C) 2025-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
def test_404(client):
    response = client.get('/404')
    assert response.status_code == 404  # Is 404
    assert b'<h1 class="title">Not Found</h1>' in response.data  # Is HTML


def test_dashboard(client):  # Is OK
    response = client.get('/')
    assert response.status_code == 200


def test_downloads(client):  # Is OK
    response = client.get('/downloaded')
    assert response.status_code == 200


def test_uploads(client):  # Is OK
    response = client.get('/uploaded')
    assert response.status_code == 200


def test_stats(client):  # Is OK
    response = client.get('/stats')
    assert response.status_code == 200


def test_infos(client):  # Is OK
    response = client.get('/info')
    assert response.status_code == 200


def test_settings(client):  # Is OK
    response = client.get('/settings')
    assert response.status_code == 200


def test_healthcheck(client):  # Is OK
    response = client.get('/healthcheck')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'


def test_translation(client):
    # Is default language
    response = client.get('/')
    assert b'<h1 class="title is-hidden">Dashboard</h1>' in response.data
    # Is defallbackfault language
    response = client.get('/', headers={'Accept-Language': 'zz'})
    assert b'<h1 class="title is-hidden">Dashboard</h1>' in response.data
    # Is fr language
    response = client.get('/', headers={'Accept-Language': 'fr'})
    assert b'<h1 class="title is-hidden">Tableau de bord</h1>' in response.data


def test_flash(app, client):
    with app.app_context():
        app.config['INIT_ERROR'] = 'Error display with flash'
        response = client.get('/')
        assert response.status_code == 200
        assert b'<li>Error display with flash</li>' in response.data
