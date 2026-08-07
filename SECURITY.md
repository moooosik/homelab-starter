# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅        |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Use GitHub's private vulnerability reporting instead:

1. Go to the [Security tab](https://github.com/moooosik/homelab-starter/security) of this repo
2. Click **"Report a vulnerability"**
3. Fill in the details — what you found, how to reproduce it, and potential impact

I'll acknowledge your report within **48 hours** and aim to release a fix within **7 days** for critical issues.

## Scope

This tool generates `docker-compose.yml` and `.env` files on the user's own machine. The main security-relevant areas are:

- Secret generation (`secrets` module usage in `compose.py`)
- Shell command execution (`subprocess` calls in `cli.py` and `docker_check.py`)
- File write paths and permissions (deploy directory creation)
- The `install.sh` one-liner (curl-pipe-bash)

Out of scope: vulnerabilities in the third-party Docker images that homelab-starter deploys. Report those directly to the upstream project.
