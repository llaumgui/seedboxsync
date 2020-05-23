---
layout: page
title: Development
description: Usage for developers
order: 4
---

## Installation

```bash
pip install -r requirements.txt

pip install setup.py
```

## Development

This project includes a number of helpers in the `Makefile` to streamline common development tasks.

### Environment Setup

The following demonstrates setting up and working with a development environment:

```bash
### create a virtualenv for development

make virtualenv

source env/bin/activate


### run seedboxsync cli application

seedboxsync --help


### run pytest / coverage

make test
```

### Releasing to PyPi

Before releasing to PyPi, you must configure your login credentials:

**~/.pypirc**:

```conf
[pypi]
username = YOUR_USERNAME
password = YOUR_PASSWORD
```

Then use the included helper function via the `Makefile`:

```bash
make dist

make dist-upload
```

## Deployments

### Docker

Included is a basic `Dockerfile` for building and distributing `SeedboxSync`,
and can be built with the included `make` helper:

```bash
make docker

docker run -it seedboxsync --help
```
