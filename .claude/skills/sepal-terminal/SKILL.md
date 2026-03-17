---
name: sepal-terminal
description: Run commands on a SEPAL sandbox via SSH. Use when you need to execute shell commands inside a SEPAL instance — system checks, process management, file operations. Requires sepal-connect for credentials.
---

# SEPAL Terminal

Run commands on a SEPAL sandbox via SSH.

## Prerequisites

- Invoke `sepal-connect` first to get credentials and determine the environment.
- `sshpass` must be installed. Check with `which sshpass`. Install with `sudo apt install sshpass` if missing.
- An active sandbox session should be running on the target environment. If SSH fails to connect, the user may need to start a sandbox from the SEPAL UI first.

## SSH Connection

All environments use port 443. SSH config aliases are defined in `~/.ssh/config`:

| Environment | SSH Alias | SSH Host | Port |
|---|---|---|---|
| local | `LOCAL_SEPAL` | `ssh.danielg.sepal.io` | 443 |
| test | `TEST_SEPAL` | `ssh.test.sepal.io` | 443 |
| prod | `SEPAL` | `ssh.sepal.io` | 443 |

## Running Commands

### Single command

```bash
sshpass -p "$SEPAL_PASSWORD" ssh -o StrictHostKeyChecking=no $SSH_ALIAS 'command here'
```

Or without alias:
```bash
sshpass -p "$SEPAL_PASSWORD" ssh -o StrictHostKeyChecking=no -p 443 "$SEPAL_USER@$SSH_HOST" 'command here'
```

### Multiple commands

Chain with `&&` (stop on failure) or `;` (run all):
```bash
sshpass -p "$SEPAL_PASSWORD" ssh $SSH_ALIAS 'cmd1 && cmd2 && cmd3'
```

### Common operations

**System health:**
```bash
sshpass -p "$SEPAL_PASSWORD" ssh $SSH_ALIAS 'df -h && free -h'
```

**Check running processes:**
```bash
sshpass -p "$SEPAL_PASSWORD" ssh $SSH_ALIAS 'ps aux | grep -E "jupyter|voila|python|solara"'
```

**List conda environments:**
```bash
sshpass -p "$SEPAL_PASSWORD" ssh $SSH_ALIAS 'conda env list'
```

**List installed apps:**
```bash
sshpass -p "$SEPAL_PASSWORD" ssh $SSH_ALIAS 'ls ~/shared/apps/'
```

## Error Handling

- **Connection refused / timeout:** Sandbox is not running. Tell the user to start one from the SEPAL UI.
- **Permission denied:** Wrong credentials. Re-run `sepal-connect`.
- **Command not found:** The command may not be available in the sandbox environment. Try with full path or activate a conda env first.

## WebSocket Fallback

If SSH is unavailable, the terminal API can be used as an alternative:
1. Get a session cookie via `sepal-connect`
2. Use `websocat` or a Node.js script to connect to `wss://$WEB_HOST/api/terminal/<uuid>?cols=120&rows=40`
3. Send commands as WebSocket text messages, receive terminal output back
4. Server sends heartbeat (empty string) every 3s — reply to keep alive

This is lower priority since SSH is the proven primary transport.
