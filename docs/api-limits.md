# API Limits

## Rate Limits by Plan

| Plan       | Requests/second | Requests/minute | Requests/month |
|------------|-----------------|-----------------|----------------|
| Free       | 2               | 60              | 10,000         |
| Starter    | 10              | 500             | 100,000        |
| Pro        | 50              | 2,000           | 1,000,000      |
| Enterprise | Custom          | Custom          | Unlimited       |

## How Rate Limits Are Enforced

Rate limits are applied per **API key**. Requests that exceed the per-second or per-minute limit receive a `429 Too Many Requests` response.

### Response Headers

Every API response includes the following headers to help you track your usage:

```
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 423
X-RateLimit-Reset: 1716825600
```

- `X-RateLimit-Limit` — the maximum number of requests allowed in the current window.
- `X-RateLimit-Remaining` — requests remaining in the current window.
- `X-RateLimit-Reset` — Unix timestamp (UTC) when the window resets.

## Handling Rate Limit Errors

When you receive a `429` response, inspect the `Retry-After` header for the number of seconds to wait before retrying.

```python
import time, requests

response = requests.get("https://api.example.com/v1/data", headers={"Authorization": "Bearer <token>"})

if response.status_code == 429:
    retry_after = int(response.headers.get("Retry-After", 1))
    time.sleep(retry_after)
```

We recommend implementing **exponential backoff with jitter** for production integrations.

## Payload and Size Limits

| Parameter         | Limit     |
|-------------------|-----------|
| Request body size | 10 MB     |
| Response body size| 50 MB     |
| Max array items   | 1,000     |
| Max string length | 65,535 characters |

## Frequently Asked Questions

**Q: Can I request a higher rate limit?**
Yes. Enterprise customers can negotiate custom limits. Contact sales@example.com with your expected request volume.

**Q: Are webhooks subject to rate limits?**
Outbound webhook deliveries do not count toward your API request quota.

**Q: Do failed requests count against my limit?**
Yes. Any request that reaches our servers — regardless of the response status — counts against your quota.
