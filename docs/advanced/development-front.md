---
title: Development frontend
summary: Development guide for SeedboxSyncFront
---
SeedboxSync also includes a frontend called SeedboxSync Front, available on [GitHub](https://github.com/llaumgui/seedboxsync-front).

## Tech Stack

* **Python 3**
* **[Flask](https://flask.palletsprojects.com/en/stable/)** / Flask-Caching / Flask-Babel / Flask-RESTX
* **[Peewee](https://docs.peewee-orm.com/en/latest/)** ORM
* **[just](https://github.com/casey/just)** as task launcher

## Frontend Development

The frontend is built with [Bulma](https://bulma.io/), [Alpine.js](https://alpinejs.dev/) and [Vite](https://vite.dev):

```bash
npm i
npm run build
```

## Python Development (Frontend Integration)

If you are working on the frontend within the Python project:

```bash
just virtualenv
source env/bin/activate
just run
```

## Development Workflow

The project includes several helpers in the `justfile` to streamline common development tasks (e.g., running the app, linting, testing).
