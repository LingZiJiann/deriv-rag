# Data Retention

## Overview

This article describes how long we retain different categories of data, your rights regarding that data, and how to request deletion.

---

## Retention Periods by Data Type

| Data Type                  | Retention Period                              |
|----------------------------|-----------------------------------------------|
| Account profile data        | Duration of account + 30 days after deletion  |
| API request logs            | 90 days                                       |
| Webhook delivery logs       | 30 days                                       |
| Audit logs (security events)| 1 year                                        |
| Payment and billing records | 7 years (legal/tax requirement)               |
| Exported data files         | 7 days after the export is ready              |
| Support ticket history      | 3 years                                       |
| Anonymized analytics        | Indefinite (no PII)                           |

---

## What Happens When You Delete Your Account

1. Your account and all associated personal data are **soft-deleted** immediately — no new requests can be made and the data is inaccessible.
2. Within **30 days**, all personal data is permanently purged from production systems.
3. Automated backup purges complete within **90 days**.
4. Billing records are retained for **7 years** to satisfy tax and financial regulations; these records are stripped of non-essential personal information.

---

## Data Export

You can export a full copy of your data at any time before deleting your account.

1. Go to **Settings > Privacy > Export my data**.
2. Click **Request export**. Processing typically takes under 1 hour.
3. You will receive an email with a secure download link. The link expires after **7 days**.

Exports include: account profile, API usage history, webhook configurations, and audit logs.

---

## GDPR / CCPA Rights

Depending on your jurisdiction, you may have the right to:

- **Access** — obtain a copy of the personal data we hold about you.
- **Rectification** — correct inaccurate data.
- **Erasure ("right to be forgotten")** — request deletion of your personal data (subject to legal retention obligations).
- **Restriction** — ask us to restrict processing of your data.
- **Portability** — receive your data in a machine-readable format.
- **Objection** — object to processing based on legitimate interests.

To exercise any of these rights, email **privacy@example.com** from the address associated with your account. We will respond within **30 days**.

---

## Data Residency

By default, data is stored in **US-East** (AWS us-east-1). Enterprise customers can request a specific region:

| Region Option   | Location            |
|-----------------|---------------------|
| US-East         | Virginia, USA       |
| EU-West         | Frankfurt, Germany  |
| AP-Southeast    | Singapore           |

Contact sales@example.com to configure a dedicated data residency agreement.

---

## Frequently Asked Questions

**Q: Can I recover data after my account is deleted?**
No. Once the 30-day soft-delete window passes, deletion is permanent and irreversible. Export your data before closing your account.

**Q: Are my API keys stored after I revoke them?**
Revoked key metadata (creation date, name, last-used timestamp) is retained in audit logs for 1 year. The key secret itself is hashed and cannot be retrieved.

**Q: How are backups handled?**
Backups are encrypted at rest (AES-256) and rotated on a 7-day cycle. Backup data follows the same retention schedule as production data and is fully purged within 90 days of account deletion.

**Q: Who can access my data?**
Access to customer data is restricted to authorized personnel on a need-to-know basis. All internal access is logged and auditable. We do not sell personal data to third parties.
