---
layout: page
title: Installation
description: How to install SeedboxSync
order: 1
---

## With pip (recommended method)

In root:

```bash
pip install seedboxsync
```

Or with simple user privileges:

```bash
pip install --user seedboxsync
```

## Clone repository

* Install script in /opt/llaumgui/seedboxsync:

```bash
sudo mkdir -p /opt/llaumgui
cd /opt/llaumgui
sudo git clone https://github.com/llaumgui/seedboxsync.git
cd seedboxsync
sudo chmod +x seedboxsync.py
```
