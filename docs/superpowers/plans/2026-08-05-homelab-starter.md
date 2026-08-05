# homelab-starter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `curl | bash` CLI that interactively bootstraps a Docker Compose homelab stack on a Linux server.

**Architecture:** Python CLI (`homelab-starter`) runs on the homelab server itself. It presents a questionary checkbox of 28 apps, asks config questions at the chosen depth (basic/guided/advanced), generates a merged `docker-compose.yml` + `.env`, and deploys via `docker compose up -d`. Watchtower is always included for auto-updates.

**Tech Stack:** Python 3.11+, Click, questionary, Rich, PyYAML, secrets (stdlib)

---

### Task 1: Package scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `homelab/__init__.py`
- Create: `.gitignore`

- [ ] Write `pyproject.toml`
- [ ] Write `homelab/__init__.py` (empty)
- [ ] Write `.gitignore`
- [ ] Commit: `chore: scaffold homelab-starter package`

---

### Task 2: App catalog

**Files:**
- Create: `homelab/apps.py` — 28 app entries with compose snippets, ports, descriptions

- [ ] Write `homelab/apps.py` with APPS dict
- [ ] Commit: `feat: app catalog with compose snippets`

---

### Task 3: Compose builder

**Files:**
- Create: `homelab/compose.py` — merge selected app dicts → docker-compose.yml + .env writer

- [ ] Write `homelab/compose.py`
- [ ] Write `tests/test_compose.py`
- [ ] Run tests
- [ ] Commit: `feat: compose file builder`

---

### Task 4: System utilities

**Files:**
- Create: `homelab/network.py` — detect local IP via socket
- Create: `homelab/docker_check.py` — validate docker + compose installed

- [ ] Write `homelab/network.py`
- [ ] Write `homelab/docker_check.py`
- [ ] Commit: `feat: network and docker utilities`

---

### Task 5: Main CLI

**Files:**
- Create: `homelab/cli.py` — full interactive flow

- [ ] Write `homelab/cli.py`
- [ ] Commit: `feat: main interactive CLI flow`

---

### Task 6: Install script + README

**Files:**
- Create: `install.sh`
- Create: `README.md`

- [ ] Write `install.sh`
- [ ] Write `README.md`
- [ ] Commit: `docs: install script and README`

---

### Task 7: GitHub push

- [ ] `git init && git add -A && git commit -m "feat: initial homelab-starter release"`
- [ ] Create GitHub repo `homelab-starter` (public)
- [ ] `git remote add origin && git push -u origin main`
