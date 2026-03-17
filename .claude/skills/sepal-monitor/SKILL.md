---
name: sepal-monitor
description: On-demand health checks and app smoke tests for SEPAL instances. Use when you need to verify apps work, check system health, or run smoke tests. Requires sepal-connect for auth and optionally sepal-terminal for system checks.
---

# SEPAL Monitor

On-demand health checks and app smoke tests for SEPAL instances.

## Prerequisites

- Invoke `sepal-connect` first to authenticate and select environment.
- For system checks: `sepal-terminal` (SSH access + active sandbox).
- For app smoke tests: session cookie from `sepal-connect`.

## System Health Checks

These require an active sandbox session and use `sepal-terminal` (SSH):

```bash
# Disk usage
sshpass -p "$SEPAL_PASSWORD" ssh $SSH_ALIAS 'df -h /'

# Memory
sshpass -p "$SEPAL_PASSWORD" ssh $SSH_ALIAS 'free -h'

# Running processes (Jupyter, Voila, Python, Solara)
sshpass -p "$SEPAL_PASSWORD" ssh $SSH_ALIAS 'ps aux | grep -E "jupyter|voila|python|solara" | grep -v grep'

# Conda environments
sshpass -p "$SEPAL_PASSWORD" ssh $SSH_ALIAS 'conda env list'

# List installed apps
sshpass -p "$SEPAL_PASSWORD" ssh $SSH_ALIAS 'ls ~/shared/apps/'
```

## App Smoke Tests

Test whether SEPAL apps load correctly via HTTP.

### Step 1: Get the app list

```bash
curl -sk -u "$SEPAL_USER:$SEPAL_PASSWORD" "https://$WEB_HOST/api/apps/list" | python3 -m json.tool
```

No auth required for this endpoint, but Basic Auth also works.

Each app has:
- `id` — unique identifier (e.g., `vector_manager`, `se.plan`)
- `endpoint` — app type: `jupyter`, `shiny`, `docker`, `rstudio`
- `path` — URL path to load the app (e.g., `/sandbox/jupyter/voila/render/shared/apps/vector_manager/ui.ipynb?voila-theme=dark&voila-template=sepal-ui-base`)
- `googleAccountRequired` — if `true`, app needs GEE credentials (flag in output)

### Step 2: Hit the app URL

Use the `SEPAL-SESSIONID` cookie from `sepal-connect`:

```bash
curl -sk -b "SEPAL-SESSIONID=$COOKIE" \
  -H "Host: $WEB_HOST" \
  "https://$WEB_HOST$APP_PATH" \
  -o /dev/null -w "HTTP %{http_code} — %{time_total}s\n"
```

- **200** — page loaded (app may still be initializing)
- **302** — redirect (may need to follow)
- **400** — endpoint not started (sandbox not running, or app type not active)
- **404** — sandbox not running (no sandbox EC2 instance active for this user)
- **500** — server error
- **502/504** — sandbox/app not running

**Important:** Jupyter/Voila/Shiny apps require an active sandbox session. If the sandbox is not running, these return 404. Docker apps (e.g., `se.plan`, `sepal_mgci`) do NOT need a sandbox and work independently.

### Step 3: Check Jupyter kernel status (Jupyter/Voila apps only)

After hitting the app URL, wait ~10-30 seconds, then check:

```bash
curl -sk -b "SEPAL-SESSIONID=$COOKIE" \
  "https://$WEB_HOST/api/sandbox/jupyter/api/kernels"
```

**Responses:**
- **200** + JSON array — sandbox is running, returns kernel list. Each kernel has `id`, `execution_state` (`idle`/`busy`/`dead`), and `name`.
- **400** + `{"message":"Endpoint must be started: jupyter"}` — sandbox is not running. The user needs to start a sandbox first.

The correct path is `/api/sandbox/jupyter/api/kernels` (not `/sandbox/jupyter/...`).

### Smoke test a specific app

To test a single app end-to-end:

1. Authenticate via `sepal-connect`
2. Find the app in `/api/apps/list` by ID
3. curl the app's `path` with `SEPAL-SESSIONID` cookie
4. Wait 10-30 seconds
5. Check kernel status (for Jupyter apps)
6. Report: app ID, HTTP status, kernel state, response time

### Smoke test all apps

Loop through `/api/apps/list`, skip `hidden` apps and external links (paths starting with `http`), and test each:

```bash
# Pseudocode — Claude should implement this as a bash loop:
for each app in apps_list:
    if app.hidden or app.path starts with "http": skip
    curl the app path with cookie
    record HTTP status and response time
    if app.endpoint == "jupyter": check kernel after delay
    if app.googleAccountRequired: flag in output
print summary table
```

### Cross-reference with module_monitor

The module_monitor project at `~/1_modules/module_monitor/` tracks migration status:
- `modules.json` — source of truth for module metadata
- Each module has `on_prod` and `on_test` deployment status
- Use `scripts/models.py` for Pydantic models (`SepalApp`, `SepalAppList`)

To correlate: match apps by `repository` URL between the API response and `modules.json`.

## API Health Checks

Quick checks that don't need a sandbox:

```bash
# Auth works
curl -sk -b "SEPAL-SESSIONID=$COOKIE" "https://$WEB_HOST/api/user/current" -w "\nHTTP %{http_code}\n"

# Apps endpoint
curl -sk "https://$WEB_HOST/api/apps/list" -o /dev/null -w "HTTP %{http_code}\n"
```

## Output Format

Present results as a summary table:

```
SEPAL Health Check — test.sepal.io
===================================

API Checks:
  /api/user/current  200 (0.3s)
  /api/apps/list     200 (0.2s)

App Smoke Tests:
  vector_manager     200 (2.1s)  jupyter  kernel: idle
  se.plan            200 (1.5s)  docker
  gfc_wrapper_python 502 (0.1s)  jupyter  [GEE required]
  ...

System (sandbox):
  Disk: 45% used
  Memory: 2.1G / 8G
  Processes: jupyter(1), voila(3)
```
