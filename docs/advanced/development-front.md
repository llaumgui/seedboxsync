---
title: Development frontend
summary: Development guide for SeedboxSyncFront
---
SeedboxSync also includes a frontend called SeedboxSync Front, available on [GitHub](https://github.com/llaumgui/seedboxsync-front).

## Tech Stack

* **Python 3**
* **Flask** / Flask-Caching / Flask-Babel / Flask-RESTX
* **Peewee** ORM

<p style="text-align:center;">
  <a href="https://www.python.org"><img alt="Python logo" src="../../images/python-powered-w-140x56.png" /></a> <a href="https://flask.palletsprojects.com"><img alt="Flask logo" src="../../images/logo-flask.png" /></a> <a href="https://docs.peewee-orm.com"><img alt="peewee logo" src="../../images/logo-peewee.png" /></a>
</p>

## Frontend Development

The frontend is built with [Bulma](https://bulma.io/), [Alpine.js](https://alpinejs.dev/) and [Vite](https://vite.dev):

```bash
npm i
npm run build
```

## Python Development (Frontend Integration)

If you are working on the frontend within the Python project:

```bash
make virtualenv
. .venv/bin/activate
make run
```

## Development Workflow

The project includes several helpers in the `Makefile` to streamline common development tasks (e.g., running the app, linting, testing).
