#
# Copyright (C) 2025-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from html.parser import HTMLParser


class FormAccessibilityParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.control_ids = []
        self.label_targets = set()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "label" and attributes.get("for"):
            self.label_targets.add(attributes["for"])
        if tag in ("input", "select") and attributes.get("type") != "hidden":
            self.control_ids.append(attributes.get("id"))


def test_404(client):
    response = client.get("/404")
    assert response.status_code == 404  # Is 404
    assert b'<h1 class="title">Not Found</h1>' in response.data  # Is HTML


def test_dashboard(client):  # Is OK
    response = client.get("/")
    assert response.status_code == 200


def test_downloads(client):  # Is OK
    response = client.get("/downloaded")
    assert response.status_code == 200


def test_uploads(client):  # Is OK
    response = client.get("/uploaded")
    assert response.status_code == 200


def test_stats(client):  # Is OK
    response = client.get("/stats")
    assert response.status_code == 200


def test_infos(client):  # Is OK
    response = client.get("/info")
    assert response.status_code == 200


def test_settings(client):  # Is OK
    response = client.get("/settings")
    assert response.status_code == 200


def test_settings_form_controls_have_associated_labels(client):
    response = client.get("/settings")
    parser = FormAccessibilityParser()
    parser.feed(response.get_data(as_text=True))

    assert None not in parser.control_ids
    assert set(parser.control_ids) <= parser.label_targets


def test_healthcheck(client):  # Is OK
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_translation_uses_accepted_language_in_auto_mode(client):
    # Uses the default language when none is requested.
    response = client.get("/")
    assert b'<html lang="en"' in response.data
    assert b'<h1 class="title is-hidden">Dashboard</h1>' in response.data

    # Falls back to the default language when the requested one is unsupported.
    response = client.get("/", headers={"Accept-Language": "zz"})
    assert b'<html lang="en"' in response.data
    assert b'<h1 class="title is-hidden">Dashboard</h1>' in response.data

    # Uses a supported requested language.
    response = client.get("/", headers={"Accept-Language": "fr"})
    assert b'<html lang="fr"' in response.data
    assert b'<h1 class="title is-hidden">Tableau de bord</h1>' in response.data


def test_translation_uses_configured_language(app, client):
    app.config["SEEDBOXSYNC_WEBUI_LANGUAGE"] = "fr"

    response = client.get("/", headers={"Accept-Language": "en"})

    assert b'<html lang="fr"' in response.data
    assert b'<h1 class="title is-hidden">Tableau de bord</h1>' in response.data


def test_flash(app, client):
    with app.app_context():
        app.config["INIT_ERROR"] = "Error display with flash"
        response = client.get("/")
        assert response.status_code == 200
        assert b"<li>Error display with flash</li>" in response.data
