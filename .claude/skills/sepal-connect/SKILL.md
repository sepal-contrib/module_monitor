---
name: sepal-connect
description: Authenticate to a SEPAL instance (local/test/prod). Use when you need to connect to SEPAL for running commands, smoke-testing apps, or checking system health. Provides session cookie and SSH credentials for other sepal-* skills.
---

# SEPAL Connect

Authenticate to a SEPAL instance and establish credentials for subsequent operations.

## Flow

1. Ask the user: **"Which SEPAL environment? (local / test / prod)"**

2. Load credentials based on selection. Check env vars first, then fall back to reading
   `~/1_modules/scripts/sepal-contrib/set_environment/my.secrets.env` (parse key=value lines, skip comments).

| Environment | Web Host | SSH Host | SSH Alias | User var | Password var |
|---|---|---|---|---|---|
| local | `danielg.sepal.io` | `ssh.danielg.sepal.io` | `LOCAL_SEPAL` | `SEPAL_USER_LOCAL` | `SEPAL_PASSWORD_LOCAL` |
| test | `test.sepal.io` | `ssh.test.sepal.io` | `TEST_SEPAL` | `SEPAL_USER_TESTENV` | `SEPAL_PASSWORD_TESTENV` |
| prod | `sepal.io` | `ssh.sepal.io` | `SEPAL` | `SEPAL_USER` | `SEPAL_PASSWORD` |

SSH port is always **443** for all environments.

3. If credentials are missing from both env and secrets file, ask the user.

4. **Get session cookie** (needed for app endpoints and browser-style APIs):

```bash
curl -sk -X POST \
  -u "$SEPAL_USER:$SEPAL_PASSWORD" \
  -H "Content-Type: application/x-www-form-urlencoded; charset=utf-8" \
  -H "No-Auth-Challenge: true" \
  -H "Host: $WEB_HOST" \
  -d "" \
  "https://$WEB_HOST/api/user/login" \
  -c -
```

Extract the `SEPAL-SESSIONID` cookie from the output. The login also returns a `JSESSIONID` but only `SEPAL-SESSIONID` works for downstream requests.

5. **Verify** the cookie works:

```bash
curl -sk -b "SEPAL-SESSIONID=$COOKIE" "https://$WEB_HOST/api/user/current"
```

Should return JSON with user details.

6. **Output** to the conversation: the environment name, web host, SSH host, username, and cookie value. These are used by `sepal-terminal` and `sepal-monitor`.

## Notes

- For read-only API calls like `/api/apps/list`, Basic Auth works directly — no cookie needed:
  ```bash
  curl -sk -u "$SEPAL_USER:$SEPAL_PASSWORD" "https://$WEB_HOST/api/apps/list"
  ```
- The secrets file path: `~/1_modules/scripts/sepal-contrib/set_environment/my.secrets.env`
- Credentials are also available as env vars if loaded via bashrc.
