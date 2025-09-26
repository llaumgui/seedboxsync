---
title: Development frontend
summary: Development guide for SeedboxSyncFront
---
SeedboxSync also includes a frontend called SeedboxSync Front, available on [GitHub](https://github.com/llaumgui/seedboxsync-front).

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
