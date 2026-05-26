# Webhooks

## Overview

Webhooks let you receive real-time HTTP notifications when events occur in your account. Instead of polling the API, you register an endpoint and we `POST` a JSON payload to it whenever a matching event fires.

---

## Setting Up a Webhook

1. Go to **Settings > Webhooks** in the dashboard.
2. Click **Add endpoint**.
3. Enter your publicly accessible HTTPS URL (e.g., `https://yourapp.com/webhooks/example`).
4. Select the **events** you want to subscribe to.
5. Save. A **signing secret** is generated — store it securely.

---

## Event Types

| Event                    | Description                                      |
|--------------------------|--------------------------------------------------|
| `payment.succeeded`      | A payment completed successfully.                |
| `payment.failed`         | A payment attempt failed.                        |
| `subscription.created`   | A new subscription was created.                  |
| `subscription.cancelled` | A subscription was cancelled.                    |
| `user.created`           | A new user account was registered.               |
| `data.export.ready`      | A requested data export is available to download.|

---

## Payload Format

All webhook payloads follow this structure:

```json
{
  "id": "evt_01HZX9KQJVT5G2B3N8P4R7",
  "type": "payment.succeeded",
  "created_at": "2026-05-26T08:14:32Z",
  "data": {
    "object": "payment",
    "id": "pay_01HZX9KQJVT5G2B3N8P4R8",
    "amount": 2900,
    "currency": "usd",
    "status": "succeeded"
  }
}
```

---

## Verifying Webhook Signatures

Every delivery includes an `X-Webhook-Signature` header. Verify it before processing the payload to confirm the request originated from us.

```python
import hmac, hashlib

def verify_signature(payload: bytes, header: str, secret: str) -> bool:
    timestamp, received_sig = header.split(",", 1)
    signed_payload = f"{timestamp}.{payload.decode()}"
    expected_sig = hmac.new(
        secret.encode(), signed_payload.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_sig, received_sig.split("=", 1)[1])
```

> Reject any request where the timestamp is older than **5 minutes** to guard against replay attacks.

---

## Retry Policy

If your endpoint returns a non-`2xx` status code or times out (30-second limit), we retry the delivery with exponential backoff:

| Attempt | Delay after previous attempt |
|---------|------------------------------|
| 1       | Immediate                    |
| 2       | 5 minutes                    |
| 3       | 30 minutes                   |
| 4       | 2 hours                      |
| 5       | 8 hours                      |

After 5 failed attempts the event is marked **failed** and no further retries are made. You can manually replay it from **Settings > Webhooks > Event log**.

---

## Best Practices

- **Respond quickly.** Return `200 OK` as soon as you receive the request and process the payload asynchronously (e.g., push to a queue).
- **Handle duplicates.** Use the `id` field to deduplicate; the same event may be delivered more than once.
- **Use HTTPS.** Plain HTTP endpoints are not accepted.
- **Rotate your signing secret** if you suspect it has been compromised.

---

## Frequently Asked Questions

**Q: Can I subscribe to all events at once?**
Yes. Select **All events** when creating the endpoint. New event types added in the future will be delivered automatically.

**Q: How long is the event log retained?**
Webhook delivery attempts are stored for **30 days** and are visible under **Settings > Webhooks > Event log**.

**Q: Can I filter events by specific resource IDs?**
Not currently. Filtering is at the event-type level. You can apply filtering logic in your own handler after receiving the payload.
