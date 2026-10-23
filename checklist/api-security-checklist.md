# API Security Checklist for REST / Web APIs

**Purpose:** A practical, defensive checklist a team can use when designing, building, reviewing or releasing a REST or web API.
**Audience:** Developers, reviewers and QA engineers.
**Scope:** Defensive controls only. All examples in this repository use a local demo with fictional data.

**How to use it**
1. Copy the checklist into a pull-request template or review ticket.
2. For every item, tick it, mark it N/A with a reason, or raise a finding.
3. "Verify by" tells you how to prove the control works. A control that was never tested should not be ticked.
4. Priority: **P1** = fix before release, **P2** = fix soon, **P3** = hardening.
5. "OWASP" maps each section to the OWASP API Security Top 10 (2023). "Demo" points to where `demo/app.py` shows the control.

---

## 1. Authentication  (OWASP API2:2023 Broken Authentication)

| # | Check | Pri | Verify by | Demo |
|---|---|---|---|---|
| 1.1 | [ ] Every endpoint requires authentication unless it is explicitly documented as public. Default is "deny". | P1 | Call each route with no credentials; expect 401 | `require_auth` |
| 1.2 | [ ] Use a standard mechanism (OAuth 2.0 / OpenID Connect, or well-reviewed signed tokens). Do not invent your own scheme. | P1 | Design review | `itsdangerous` signed tokens |
| 1.3 | [ ] Access tokens are short-lived and expiry is enforced server-side. Refresh tokens (if used) are rotated and revocable. | P1 | Replay an expired token; expect 401 | `TOKEN_TTL_SECONDS` |
| 1.4 | [ ] Token signatures are verified on every request. If JWTs are used: pin the allowed algorithm, reject `alg: none`, validate `iss`, `aud`, `exp`. | P1 | Send a tampered / unsigned token | `test_tampered_token_is_401` |
| 1.5 | [ ] Credentials are never sent in URLs or query strings (they leak into logs, history and referrers). Use the `Authorization` header. | P1 | Grep logs and code | header-only auth |
| 1.6 | [ ] Passwords are stored with a slow, salted hash (Argon2id, scrypt or bcrypt). Never plain text or fast hashes. | P1 | Code review | `generate_password_hash` |
| 1.7 | [ ] Login returns the same response for "unknown user" and "wrong password", and takes similar time. | P2 | Compare responses | dummy hash check |
| 1.8 | [ ] Login, password reset and token endpoints have stricter rate limits and lockout/back-off. Prefer MFA for sensitive accounts. | P1 | Send repeated bad logins; expect 429 | `RATE_LIMIT_LOGIN` |
| 1.9 | [ ] 401 responses include `WWW-Authenticate`; failures never reveal *why* a token failed in detail. | P3 | Inspect headers | `require_auth` |
| 1.10 | [ ] API keys (if used) identify the calling application, are scoped, rotatable and never embedded in client-side code. | P2 | Design review | N/A in demo |
| 1.11 | [ ] Sessions/tokens are invalidated on logout, password change and account disablement (for JWTs, deny-list the token ID until it expires). | P2 | Functional test | not implemented (noted in limitations) |
| 1.12 | [ ] Password policy follows current NIST guidance (SP 800-63B-4): allow long passwords (64+ characters), no forced composition rules or periodic changes, block common/compromised passwords, rate-limit failed attempts. | P2 | Policy review; try a known-breached password | demo accounts use long fictional passwords; blocklist not implemented |

## 2. Authorisation  (OWASP API1 BOLA, API3 BOPLA, API5 BFLA)

### 2a. Object-level authorisation (most important for APIs)

| # | Check | Pri | Verify by | Demo |
|---|---|---|---|---|
| 2.1 | [ ] Every request that takes an object ID (path, query, body, header) checks that **the authenticated caller may access that specific object**. | P1 | User A requests user B's object; expect denial | `get_note` |
| 2.2 | [ ] The check is done on the server using the identity from the token, never from a user-supplied `user_id` / `owner` field. | P1 | Send a body containing another user's ID | `create_note` ignores body owner |
| 2.3 | [ ] List/search endpoints are scoped to the caller in the query itself, not filtered after loading everything. | P1 | Compare lists for two users | `list_notes` |
| 2.4 | [ ] Use hard-to-guess identifiers (UUIDs) as defence in depth. This does **not** replace the check in 2.1. | P3 | Review | `uuid4` IDs |
| 2.5 | [ ] Return the same response for "not found" and "not yours" so attackers cannot enumerate valid IDs. | P2 | Compare responses | `test_missing_and_foreign_notes_look_identical` |
| 2.6 | [ ] Write operations (PUT/PATCH/DELETE) get the same ownership check as reads. | P1 | Test each verb | `delete_note` |
| 2.7 | [ ] Authorisation logic is centralised (middleware, policy layer), not copy-pasted per endpoint. | P2 | Code review | partially (helper pattern) |

### 2b. Function-level and property-level authorisation

| # | Check | Pri | Verify by | Demo |
|---|---|---|---|---|
| 2.8 | [ ] Administrative or privileged endpoints require an explicit role/scope check; a normal user calling them gets 403. | P1 | Call admin routes as normal user | N/A (no admin routes) |
| 2.9 | [ ] Each HTTP method is authorised separately (a user allowed to GET may not be allowed to DELETE). | P1 | Test each method | per-route decorators |
| 2.10 | [ ] Responses return only an explicit allow-list of fields. Internal fields (flags, hashes, internal IDs) never leave the server. | P1 | Inspect responses | `public_note` |
| 2.11 | [ ] Request bodies are bound to an allow-list of writable fields (prevents mass assignment such as `is_admin: true`). | P1 | Send extra fields; expect 400 | `validate_note_payload` |

## 3. Input Validation  (OWASP API3, API8; injection classes)

| # | Check | Pri | Verify by | Demo |
|---|---|---|---|---|
| 3.1 | [ ] Validate everything from the client: body, path, query, headers, cookies, file uploads. Treat all of it as untrusted. | P1 | Review each input | all handlers |
| 3.2 | [ ] Use an allow-list schema (JSON Schema, OpenAPI, Pydantic, etc.): type, length, range, format, enum. Reject unknown fields. | P1 | Send wrong types / extra fields | `validate_note_payload` |
| 3.3 | [ ] Enforce `Content-Type` and reject mismatches with 415. | P2 | Send form data to a JSON route | `start_request` |
| 3.4 | [ ] Enforce a maximum request body size; reject with 413. | P1 | Send an oversized body | `MAX_CONTENT_LENGTH` |
| 3.5 | [ ] Use parameterised queries / ORM bindings. Never build SQL, NoSQL, LDAP or OS commands by string concatenation. | P1 | Code review, SAST | N/A (in-memory data) |
| 3.6 | [ ] Validate pagination parameters and cap them (`limit` maximum, sane `offset`). | P2 | Send `limit=1000000` | `list_notes` |
| 3.7 | [ ] Parse IDs strictly (for example, UUID format) and return a clean 4xx on bad format, not a 500. | P2 | Send `not-a-uuid` | `parse_uuid` |
| 3.8 | [ ] Validate on the server even if a client or gateway already validated. | P1 | Bypass client | server-side only |
| 3.9 | [ ] If the API fetches a URL supplied by a client (webhooks, image import), restrict to allow-listed hosts and block internal address ranges (SSRF, API7). | P1 | Review | N/A |
| 3.10 | [ ] Set explicit response `Content-Type` and `X-Content-Type-Options: nosniff`. | P3 | Inspect headers | `finish_request` |
| 3.11 | [ ] Treat data from third-party APIs as untrusted too: validate it, set timeouts, limit redirects and response sizes (API10). | P2 | Review | N/A |

## 4. Rate Limiting and Resource Consumption  (OWASP API4, API6)

| # | Check | Pri | Verify by | Demo |
|---|---|---|---|---|
| 4.1 | [ ] Apply rate limits per client identity (user, API key, IP), at the gateway or in the app. | P1 | Burst test on your own local instance | `rate_limited` |
| 4.2 | [ ] Use stricter limits for expensive or sensitive endpoints (login, search, export, SMS/email sending). | P1 | Burst test | `RATE_LIMIT_LOGIN` |
| 4.3 | [ ] Return `429 Too Many Requests` and include `Retry-After` (RFC 6585 makes the header optional, but it helps well-behaved clients back off). | P2 | Inspect response | `test_429_has_retry_after` |
| 4.4 | [ ] Set request-size, pagination, timeout and concurrency limits. Cap upload sizes and query complexity (including GraphQL depth if used). | P1 | Review config | `MAX_CONTENT_LENGTH`, `limit` cap |
| 4.5 | [ ] Protect sensitive business flows (purchase, signup, coupon, ticketing) against automation and abuse with quotas or step-up checks. | P2 | Threat model | N/A |
| 4.6 | [ ] Set cost controls on paid downstream services (SMS, AI calls, cloud functions) so abuse cannot cause a bill spike. | P3 | Review | N/A |
| 4.7 | [ ] Production limits are stored in a shared store (for example Redis) or enforced at an API gateway so they work across multiple instances. | P2 | Architecture review | in-memory only (limitation) |

## 5. Error Handling  (OWASP API8 Security Misconfiguration)

| # | Check | Pri | Verify by | Demo |
|---|---|---|---|---|
| 5.1 | [ ] Use a consistent error format (for example RFC 9457 Problem Details or a simple `{code, message, request_id}`). | P3 | Inspect responses | `error()` |
| 5.2 | [ ] Never return stack traces, SQL errors, file paths, framework versions or internal hostnames to clients. | P1 | Trigger an exception | `handle_unexpected` |
| 5.3 | [ ] Log full detail server-side; give clients a generic message plus a request ID for support. | P1 | Compare client and server output | `X-Request-ID` |
| 5.4 | [ ] Use correct status codes: 400/422 validation, 401 unauthenticated, 403 forbidden, 404 not found, 409 conflict, 413, 415, 429, 5xx. | P2 | Contract tests | handlers |
| 5.5 | [ ] Error messages do not reveal whether an account, email or object exists. | P2 | Compare responses | login + 404 |
| 5.6 | [ ] Run with debug mode off in production. Disable verbose framework error pages. | P1 | Check config | `debug=False` |
| 5.7 | [ ] Fail closed: if an authorisation or validation component errors, deny the request. | P1 | Fault-injection test | `handle_unexpected` returns 500, no data |

## 6. Transport Security  (OWASP API8)

| # | Check | Pri | Verify by | Demo |
|---|---|---|---|---|
| 6.1 | [ ] All API traffic uses HTTPS. Plain HTTP is disabled or only redirects (and never serves data). | P1 | `curl -I http://...` against your own host | demo runs on local HTTP (limitation) |
| 6.2 | [ ] Allow TLS 1.2+ only (prefer 1.3). Disable SSL, TLS 1.0 and 1.1 and weak cipher suites. | P1 | TLS scan of **your own** endpoint | proxy responsibility |
| 6.3 | [ ] Certificates are valid, trusted, renewed automatically and monitored for expiry. Consider CAA DNS records to limit which CAs may issue for your domain. | P1 | Monitoring | proxy responsibility |
| 6.4 | [ ] Send `Strict-Transport-Security` on HTTPS responses. | P2 | Inspect headers | `finish_request` |
| 6.5 | [ ] Internal service-to-service traffic is encrypted too (TLS or mTLS), not just the public edge. | P2 | Architecture review | N/A |
| 6.6 | [ ] Clients validate server certificates. Never disable verification (`verify=False`) in code. | P1 | Code search | N/A |
| 6.7 | [ ] Set `Cache-Control: no-store` on responses containing personal or sensitive data. | P2 | Inspect headers | `finish_request` |
| 6.8 | [ ] CORS: allow only specific trusted origins, never `*` together with credentials; limit methods and headers. | P2 | Test with a disallowed origin | no CORS enabled (default deny) |
| 6.9 | [ ] Add `Content-Security-Policy: frame-ancestors 'none'` (and `X-Frame-Options: DENY` for older browsers) on any response a browser may render. | P3 | Inspect headers | CSP only in `finish_request` |

## 7. Secrets Management  (OWASP API8 / ASVS V6)

| # | Check | Pri | Verify by | Demo |
|---|---|---|---|---|
| 7.1 | [ ] No secrets (keys, passwords, tokens, connection strings) in source code or git history. | P1 | Secret scanner (gitleaks, truffleHog) on repo | key read from env |
| 7.2 | [ ] Load secrets from environment variables or a secrets manager (Vault, cloud secret manager), injected at runtime. | P1 | Review deployment | `DEMO_SECRET_KEY` |
| 7.3 | [ ] `.env` files and key files are listed in `.gitignore`. Commit only a `.env.example` with fake values. | P1 | Check repo | `.gitignore` |
| 7.4 | [ ] Secrets are rotated regularly and immediately after suspected exposure. A rotation procedure exists and has been tried. | P2 | Run a rotation drill | N/A |
| 7.5 | [ ] Use separate secrets per environment (dev/test/prod) and least-privilege credentials per service. | P2 | Review | N/A |
| 7.6 | [ ] Secrets never appear in logs, error messages, URLs or client-side bundles. | P1 | Log review | `test_logs_do_not_contain_secrets` |
| 7.7 | [ ] Enable push protection / secret scanning in the repository host and CI. | P2 | Check settings | N/A |
| 7.8 | [ ] If a random key is generated at start-up (as in the demo), understand that tokens die on restart. In production use a persistent managed key. | P3 | Review | fallback in `SECRET_KEY` |

## 8. Logging and Monitoring  (OWASP API8; ASVS V7)

| # | Check | Pri | Verify by | Demo |
|---|---|---|---|---|
| 8.1 | [ ] Log security-relevant events: login success/failure, token failures, authorisation denials, rate-limit hits, validation failures, admin actions. | P1 | Trigger events; check logs | request log line |
| 8.2 | [ ] Each log entry has time, request ID, caller ID, method, path, status and source IP. | P2 | Log review | `finish_request` |
| 8.3 | [ ] **Never** log passwords, tokens, API keys, full card numbers or personal data. Mask or omit. Avoid logging query strings and bodies by default. | P1 | Test + grep | `test_logs_do_not_contain_secrets` |
| 8.4 | [ ] Prevent log injection: do not write raw user input containing newlines into log lines. Use structured (JSON) logging. | P2 | Send CRLF in a field | partial (limitation) |
| 8.5 | [ ] Ship logs to a central, access-controlled, tamper-resistant store with retention rules. | P2 | Architecture review | N/A |
| 8.6 | [ ] Alert on abnormal patterns: spikes in 401/403/404/429, enumeration across many IDs, access from unusual places. | P2 | Alert test | N/A |
| 8.7 | [ ] Correlate client-visible `request_id` with server logs to speed up investigation. | P3 | Follow one request end to end | `X-Request-ID` |
| 8.8 | [ ] Define an incident-response path: who is paged, how tokens are revoked, how keys are rotated. | P2 | Tabletop exercise | N/A |

## 9. Versioning, Deprecation and Inventory  (OWASP API9 Improper Inventory Management)

| # | Check | Pri | Verify by | Demo |
|---|---|---|---|---|
| 9.1 | [ ] Keep an inventory of all API hosts, versions, environments and endpoints, including internal, beta and forgotten ones. | P1 | Compare gateway logs with the inventory | `/api/v0`, `/api/v1` |
| 9.2 | [ ] Version the API explicitly (`/v1/` in the path or a version header). | P2 | Design review | `/api/v1/...` |
| 9.3 | [ ] Publish a deprecation policy: announcement lead time, sunset date, migration guide. | P2 | Docs review | `Sunset` header |
| 9.4 | [ ] Signal deprecation in responses with the `Deprecation` header (RFC 9745) and `Sunset` header (RFC 8594), plus `Link` headers: `rel="deprecation"` (RFC 9745) for the migration notice and `rel="successor-version"` (RFC 5829) for the new version. | P3 | Inspect old-version responses | `finish_request` (successor link only) |
| 9.5 | [ ] Old versions receive security fixes until sunset, then are **actually shut down** (return 410 Gone or remove). | P1 | Call retired version | `/api/v0` (kept to demo headers) |
| 9.6 | [ ] Non-production environments (staging, test, debug endpoints) are not reachable from the internet or are protected like production. They never hold real data. | P1 | External scan of your own scope | N/A |
| 9.7 | [ ] Maintain an up-to-date OpenAPI specification and use it for validation and contract tests. Detect drift between spec and reality. | P2 | CI check | N/A |
| 9.8 | [ ] Remove unused endpoints, methods and fields (for example, disable `TRACE`/unused verbs). | P2 | Route audit | explicit methods only |
| 9.9 | [ ] Track dependencies and patch them: run SCA / dependency scanning in CI (`pip-audit`, `npm audit`, Dependabot). | P1 | CI report | `requirements.txt` |

## 10. Pre-Release Sign-Off

- [ ] All P1 items are ticked or have an approved, dated exception.
- [ ] Automated tests cover items 1.1, 1.3, 2.1, 2.11, 3.2, 3.4, 4.3, 5.2 and 8.3 at minimum.
- [ ] Testing was done **only** on systems you own or are explicitly authorised to test.
- [ ] Secrets scan is clean; dependency scan reviewed.
- [ ] Threat model and endpoint inventory are updated.
- [ ] Reviewer name and date recorded: ____________________

---

### Quick reference: OWASP API Security Top 10 (2023) mapping

| OWASP risk | Checklist sections |
|---|---|
| API1 Broken Object Level Authorization | 2a |
| API2 Broken Authentication | 1 |
| API3 Broken Object Property Level Authorization | 2b, 3 |
| API4 Unrestricted Resource Consumption | 4, 3.4, 3.6 |
| API5 Broken Function Level Authorization | 2b |
| API6 Unrestricted Access to Sensitive Business Flows | 4.5 |
| API7 Server-Side Request Forgery | 3.9 |
| API8 Security Misconfiguration | 5, 6, 7, 8 |
| API9 Improper Inventory Management | 9 |
| API10 Unsafe Consumption of APIs | 3.11 |

See `../references.md` for sources.
