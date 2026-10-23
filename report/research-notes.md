# Research Notes: API Security Checklist

Compiled 14 October 2026. Every page below was opened and read on that date; summaries are paraphrased. Re-open the links yourself before submitting and keep your own "accessed" dates.

## 1. What was checked and what it means for the checklist

| Source | What it says (paraphrased) | Effect on this project |
|---|---|---|
| OWASP API Security Top 10 (2023) | Ten risks: API1 Broken Object Level Authorization, API2 Broken Authentication, API3 Broken Object Property Level Authorization, API4 Unrestricted Resource Consumption, API5 Broken Function Level Authorization, API6 Unrestricted Access to Sensitive Business Flows, API7 Server Side Request Forgery, API8 Security Misconfiguration, API9 Improper Inventory Management, API10 Unsafe Consumption of APIs | Confirms the OWASP mapping table in the checklist |
| OWASP REST Security Cheat Sheet | HTTPS only; access control on every non-public endpoint; JWT checks (reject unsigned tokens, take the algorithm from your own config, validate `iss`/`aud`/`exp`, deny-list token ID on logout); explicit allow-list of HTTP methods (405 otherwise); validate input and cap request size (413); require a supported `Content-Type` (415); correct status codes; generic errors; browser-oriented security headers including `X-Frame-Options: DENY`; restrictive CORS; audit logging with sanitised log data | Matches the demo. Added a note about token deny-listing (1.11) and `X-Frame-Options` (6.9) to the checklist |
| OWASP Logging Cheat Sheet | Log validation, authentication, authorisation and session failures plus privileged actions; never log credentials, tokens, keys or connection strings; avoid raw session IDs; mask personal data; sanitise CR/LF to stop log injection; protect log integrity | Supports section 8; 8.4 and 8.3 kept |
| OWASP Secrets Management Cheat Sheet | Central secrets manager, automated rotation, least privilege, treat CI/CD as production, scan for leaks early (and with more than one tool), audit secret access, documented response to exposure | Supports section 7 |
| OWASP TLS Cheat Sheet | Default to TLS 1.3, TLS 1.2 only where needed for compatibility; disable TLS 1.0/1.1 and SSL; AEAD cipher suites; HSTS plus redirect; RSA keys of at least 2048 bits; CAA records | Matches 6.2; CAA mentioned in 6.3 |
| NIST SP 800-228 | Guidelines for API protection in cloud-native systems: risks across development and runtime, baseline and advanced controls, trade-offs between implementation options. **The June 2025 version was withdrawn on 13 March 2026 and replaced by an updated final version that adds two appendices (API risks by category; recommended controls by lifecycle stage).** | **Corrected the reference URL** to the updated version |
| NIST SP 800-63B-4 | Passwords used alone: minimum 15 characters (8 if only part of multi-factor); allow at least 64 characters; no composition rules; check against blocklists of common/compromised passwords; no forced periodic changes; failed authentication attempts must be rate-limited | **Added checklist item 1.12** (password policy) |
| NIST SP 800-52 Rev. 2 | TLS guidance (August 2019); requires TLS 1.2 support and TLS 1.3 support from 1 January 2024 for US government systems. NIST notes the publication is under review (note dated May 2026) | Kept as reference with a "under review" caveat |
| RFC 9745 (March 2025) | Defines the `Deprecation` response header. Its value is a Structured Fields Date, written like `@1688169599`. It does not change how the resource behaves. It also defines the `deprecation` link relation for pointing at documentation | Demo's header format is correct. Added the `deprecation` link relation to the checklist note |
| RFC 8594 | `Sunset` header gives the date after which a resource is expected to stop responding, in normal HTTP-date format. Per RFC 9745, the Sunset date should not be earlier than the Deprecation date | Demo's dates (Deprecation 2026-01-01, Sunset 2027-03-31) are consistent |
| RFC 5829 (April 2010) | Defines the `successor-version` link relation (and `latest-version`, `predecessor-version`, etc.) | **Correction:** `successor-version` comes from RFC 5829, not RFC 9745. Reference added |
| RFC 6585 | 429 response *may* include `Retry-After`; the RFC does not say how to identify the client or count requests | Checklist keeps "include Retry-After" as good practice, not a mandatory rule |
| OWASP ASVS | The OWASP project page names 5.0.0 as the latest version but labels it inconsistently ("latest stable" vs "bleeding edge"). 4.0.3 (2021) is the previous stable release | Cite as "ASVS" with the version you actually read |

### Things that were wrong or imprecise in my earlier draft (now fixed)
1. NIST SP 800-228 link pointed at the withdrawn June 2025 version.
2. `successor-version` was implied to come from the deprecation RFCs; it is from RFC 5829.
3. NIST SP 800-63B title in `references.md` used the older wording; now cites SP 800-63B-4.

## 2. Real-world incidents (for the "why it matters" section)

Use these as short motivating examples. Describe them as reported, not as your own findings.

| Incident | What is documented | Relevant checklist sections |
|---|---|---|
| **Peloton, 2021** | A researcher at Pen Test Partners reported in January 2021 that Peloton's API returned account details, including details for private profiles, without properly checking whether the requester was allowed to see them. Requiring a paid membership did not help because anyone could sign up. Peloton later confirmed a fix after press contact. Source: TechCrunch, 5 May 2021 | 1, 2 (object-level authorisation), 9 |
| **T-Mobile, 2023** | In an SEC Form 8-K dated 19 January 2023, T-Mobile said it detected on 5 January 2023 that a malicious actor had obtained data through a single API without authorisation, affecting about 37 million customer accounts, with access beginning around 25 November 2022. The filing does not state the technical root cause, so do not assume one | 1, 2, 4 (rate limits), 8 (detection and monitoring) |
| **Optus, 2022 (allegation)** | The Australian communications regulator (ACMA) alleges in court filings that a 2018 coding error disabled access controls on internet-facing systems, which later exposed customer data (about 9.5 million records accessed). Optus disputes this explanation, and no court finding was reported in the article read. Treat it only as an allegation | 2, 5, 9 (inventory: dormant domain not decommissioned) |

## 3. Synthesis

API security depends on controls at multiple layers. Application code must enforce authentication, per-object authorisation and input validation; the hosting platform must provide transport security and shared infrastructure such as gateways and secrets managers; and the organisation must maintain endpoint inventories, deprecation processes and monitoring. The checklist pairs each recommendation with a verification method because an untested control is only an assumption.

## 4. Research scope and caveats

- These notes record a point-in-time literature review compiled on 14 October 2026. Re-check source links and publication status before relying on them for later work.
- The OWASP ASVS project page is included as general verification guidance; this project does not claim conformance to a particular ASVS version.
- NIST SP 800-63B-4 is cited for its password recommendations without making a separate claim about its publication-status label.
- The Optus account is reported as an allegation disputed by Optus; it is not presented as a court-established finding.
- The reported incidents provide context only. No real system was tested as part of this project.
- No experiment was performed by disabling a security control. Results in the technical report are from the implemented demo and its tests.

## 5. Source list (read on 14 Oct 2026)
- OWASP API Security Top 10 2023: https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- OWASP REST Security Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html
- OWASP Logging Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- OWASP TLS Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html
- NIST SP 800-228 (updated final): https://csrc.nist.gov/pubs/sp/800/228/upd1/final
- NIST SP 800-52 Rev. 2: https://csrc.nist.gov/pubs/sp/800/52/r2/final
- NIST SP 800-63B-4: https://pages.nist.gov/800-63-4/sp800-63b.html
- RFC 9745: https://www.rfc-editor.org/rfc/rfc9745.html
- RFC 5829: https://www.rfc-editor.org/rfc/rfc5829.html
- RFC 6585: https://www.rfc-editor.org/rfc/rfc6585.html
- OWASP ASVS project page: https://owasp.org/projects/asvs?tab=main
- T-Mobile Form 8-K (19 Jan 2023): https://www.sec.gov/Archives/edgar/data/1283699/000119312523010949/d641142d8k.htm
- TechCrunch, Peloton API (5 May 2021): https://techcrunch.com/2021/05/05/peloton-bug-account-data-leak/
- CSO Online, Optus/ACMA allegation: https://www.csoonline.com/article/2492520/optus-breach-occurred-due-to-a-coding-error-alleges-acma.html
