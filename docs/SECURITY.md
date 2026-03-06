# LifeOS Security Guide

## Security Model

LifeOS is a **single-user, local network application**. Its security model is:

> *Protect from the open internet. Trust the local network.*

This means:
- **No authentication** — the app assumes only trusted users are on your home network
- **No TLS/HTTPS** — acceptable for LAN-only use (all traffic stays inside your router)
- **No rate limiting** — not needed for personal single-user use
- **No CSRF tokens** — acceptable for LAN-only, same-origin HTMX usage

This is a deliberate trade-off for simplicity. If your threat model requires stronger security (e.g. you want to expose this over the internet), see the [Hardening](#hardening-for-remote-access) section.

---

## What is Protected

### SQL Injection
All database access uses SQLAlchemy's parameterized queries via the ORM. No raw SQL strings are ever constructed with user input.

```python
# Safe — parameterized
stmt = select(Goal).where(Goal.id == goal_id)

# Never done — vulnerable
stmt = f"SELECT * FROM goals WHERE id = {goal_id}"
```

### XSS (Cross-Site Scripting)
Jinja2 auto-escapes all template variables by default. User-provided strings rendered in templates are safe.

```html
<!-- Safe — Jinja2 escapes this -->
<span>{{ task.title }}</span>

<!-- Would be unsafe — never done -->
<span>{{ task.title | safe }}</span>
```

### Path Traversal
Static files are served from a fixed directory via FastAPI's `StaticFiles`. User input never constructs file paths.

### Dependency Pinning
All dependencies in `pyproject.toml` use minimum version pins (`>=`). For production-style deployment, pin exact versions:
```bash
pip freeze > requirements-lock.txt
```

---

## What is NOT Protected (by Design)

| Threat | Status | Rationale |
|--------|--------|-----------|
| Unauthenticated access | Unprotected | Local network trust model |
| Brute force | Unprotected | No login form to brute force |
| HTTPS interception | Unprotected | LAN traffic only |
| CSRF | Unprotected | Same-origin HTMX, LAN only |
| Denial of Service | Unprotected | Single-user personal use |

---

## Network Configuration

### Recommended Setup (Home Use)

```
Internet
    │
  Router / NAT (firewall)
    │
  Home LAN (192.168.x.x)
    │
  Your PC running LifeOS on port 8000
```

**The router's NAT is your primary protection.** As long as you don't forward port 8000 to the internet, the app is only accessible from devices inside your home.

### Binding

The app binds to `0.0.0.0:8000` by default (all interfaces on your machine). This is intentional for LAN access.

To restrict to localhost only:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

## Hardening for Remote Access

If you want to access LifeOS outside your home network, **do not expose port 8000 directly to the internet**. Instead use one of these approaches:

### Option 1: VPN (Recommended)

Set up WireGuard or Tailscale on your home machine. Access LifeOS through the VPN tunnel.

```bash
# Tailscale (easiest)
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# Then access: http://<tailscale-ip>:8000
```

### Option 2: Reverse Proxy with Authentication

Use Nginx as a reverse proxy with HTTP Basic Auth:

```nginx
# /etc/nginx/sites-available/lifeos
server {
    listen 443 ssl;
    server_name lifeos.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/lifeos.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/lifeos.yourdomain.com/privkey.pem;

    auth_basic "LifeOS";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Generate a password:
```bash
sudo htpasswd -c /etc/nginx/.htpasswd yourname
```

### Option 3: SSH Tunnel

```bash
# From your remote machine, tunnel port 8000 over SSH
ssh -L 8000:localhost:8000 youruser@your-home-ip
# Then access: http://localhost:8000
```

---

## Database Security

### Location
The SQLite database is stored at `db/lifeos.db`. It is excluded from git via `.gitignore`.

### Backup
```bash
# Manual backup
cp db/lifeos.db db/lifeos.backup.$(date +%Y%m%d).db

# Automated daily backup (add to crontab)
0 2 * * * cp /path/to/lifeos/db/lifeos.db /path/to/backup/lifeos.$(date +\%Y\%m\%d).db
```

### Permissions
```bash
# Restrict DB file permissions
chmod 600 db/lifeos.db
```

---

## Logging

LifeOS uses `structlog` for structured logging. Logs go to stdout by default.

To log to a file, redirect uvicorn output:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 >> logs/lifeos.log 2>&1
```

Logs do **not** include request bodies (which may contain task titles etc.). Only structured events like `goal_created`, `task_updated` are logged.

---

## Dependency Vulnerabilities

Check for known vulnerabilities:
```bash
pip install pip-audit
pip-audit
```

Update dependencies:
```bash
pip install --upgrade -e ".[dev]"
```

---

## Running as a Non-Root Service (Linux)

```bash
# Create a systemd service
sudo nano /etc/systemd/system/lifeos.service
```

```ini
[Unit]
Description=LifeOS Personal Productivity App
After=network.target

[Service]
Type=simple
User=johnsmith
WorkingDirectory=/home/johnsmith/github/lifeos
ExecStart=/home/johnsmith/github/lifeos/myenv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable lifeos
sudo systemctl start lifeos
sudo systemctl status lifeos
```

This runs LifeOS as your user (not root), restarts on crash, and starts on boot.

---

## Reporting Issues

This is a personal project. If you find a security issue, open a GitHub Issue with the `security` label.
