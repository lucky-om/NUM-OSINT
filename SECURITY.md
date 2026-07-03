# Security Policy

**NUM-OSINT** — Developed by Lucky  
Telegram: @universeluckyy | Website: luckyverse.tech

---

## Reporting a Vulnerability

If you discover a security vulnerability in NUM-OSINT, please report it
**privately** — do NOT open a public issue.

Contact the developer directly:

| Channel | Details |
|---|---|
| Telegram | [@universeluckyy](https://t.me/universeluckyy) |
| Website | [luckyverse.tech](https://luckyverse.tech) |

Please include:
- A clear description of the vulnerability
- Steps to reproduce it
- Potential impact

You will receive a response within **48 hours**. Valid reports will be
credited publicly if you wish.

---

## Security Design

- **Access control** — The tool requires a security key at startup.
  The key is never stored in plain text; it is verified using a
  cryptographic hash.
- **API protection** — API endpoints are not visible in plain text
  within the source code.
- **No data storage** — The tool does not write, cache, or log any
  queried data to disk.
- **No telemetry** — No usage data is collected or transmitted.

---

## Scope

| In Scope | Out of Scope |
|---|---|
| Authentication bypass | Issues with third-party APIs |
| Source-code exposure of secrets | Feature requests |
| Logic vulnerabilities | Data accuracy from APIs |

---

## Legal

Responsible disclosure is appreciated. Any attempt to exploit, reverse-engineer,
or misuse this tool is a violation of the license agreement and may be subject
to legal action.

© 2026 Lucky. All Rights Reserved.
