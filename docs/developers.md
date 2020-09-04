---
layout: page
title: Development
description: Usage for developers
order: 4
---

SeedboxSync is build with [Cement](https://builtoncement.com/) and [Peewee](http://docs.peewee-orm.com/en/latest/) from v3.

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
