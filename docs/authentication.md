# Authentication

## Overview

All API requests must be authenticated. We support two authentication methods:

| Method        | Use case                                |
|---------------|-----------------------------------------|
| API Key       | Server-to-server integrations           |
| OAuth 2.0     | User-facing applications (act on behalf of a user) |

---

## API Key Authentication

### Obtaining an API Key

1. Log in to the dashboard at **app.example.com**.
2. Navigate to **Settings > API Keys**.
3. Click **Create new key**, give it a name, and choose the desired permissions scope.
4. Copy the key immediately — it will not be shown again.

### Using an API Key

Pass the key in the `Authorization` header of every request:

```http
GET /v1/resource HTTP/1.1
Host: api.example.com
Authorization: Bearer sk_live_xxxxxxxxxxxxxxxxxxxx
```

### Key Prefixes

| Prefix       | Environment |
|--------------|-------------|
| `sk_live_`   | Production  |
| `sk_test_`   | Sandbox/test|

> **Never expose API keys in client-side code or public repositories.** Use environment variables or a secrets manager.

### Rotating and Revoking Keys

Keys can be rotated or revoked at any time from **Settings > API Keys**. Revoking a key immediately invalidates it; any in-flight requests using the revoked key will fail with `401 Unauthorized`.

---

## OAuth 2.0 Authentication

Use OAuth 2.0 when your application needs to act on behalf of an end user.

### Supported Grant Types

- **Authorization Code** (recommended for web apps)
- **PKCE** (recommended for mobile and SPA apps)
- **Client Credentials** (machine-to-machine, no user context)

### Authorization Code Flow

1. **Redirect the user** to the authorization endpoint:
   ```
   https://auth.example.com/oauth/authorize
     ?client_id=YOUR_CLIENT_ID
     &redirect_uri=https://yourapp.com/callback
     &response_type=code
     &scope=read:data write:data
     &state=RANDOM_STATE_VALUE
   ```

2. **Exchange the code** for an access token:
   ```http
   POST /oauth/token HTTP/1.1
   Host: auth.example.com
   Content-Type: application/x-www-form-urlencoded

   grant_type=authorization_code
   &code=AUTHORIZATION_CODE
   &redirect_uri=https://yourapp.com/callback
   &client_id=YOUR_CLIENT_ID
   &client_secret=YOUR_CLIENT_SECRET
   ```

3. **Use the access token** in subsequent API calls:
   ```http
   Authorization: Bearer ACCESS_TOKEN
   ```

### Token Lifetimes

| Token         | Lifetime    |
|---------------|-------------|
| Access token  | 1 hour      |
| Refresh token | 30 days     |

Use the refresh token to obtain a new access token before expiry without requiring the user to re-authenticate.

---

## Frequently Asked Questions

**Q: What happens when an API key is compromised?**
Revoke it immediately from the dashboard and generate a new key. Review your access logs under **Settings > Audit Log** for any unauthorized activity.

**Q: Can I restrict an API key to specific IP addresses?**
Yes. When creating or editing a key, expand **Advanced settings** and add IP allowlist entries (CIDR notation supported).

**Q: How do I test authentication without hitting production?**
Use a `sk_test_` key. Requests made with test keys are processed in the sandbox environment and never affect live data.
