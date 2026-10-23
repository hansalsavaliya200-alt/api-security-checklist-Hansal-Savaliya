# References

Web sources were read between 14 and 24 October 2026. A summary of what each source says and how it was used is in [`report/research-notes.md`](report/research-notes.md).

Format: Author/Publisher. *Title.* Date or version. URL.

---

## 1. Standards and guidance

### 1.1 OWASP

1. OWASP Foundation. *OWASP API Security Top 10 – 2023.* 2023. https://owasp.org/API-Security/editions/2023/en/0x11-t10/
2. OWASP Cheat Sheet Series. *REST Security Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html
3. OWASP Cheat Sheet Series. *Authentication Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
4. OWASP Cheat Sheet Series. *Authorization Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
5. OWASP Cheat Sheet Series. *Insecure Direct Object Reference Prevention Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html
6. OWASP Cheat Sheet Series. *Mass Assignment Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html
7. OWASP Cheat Sheet Series. *Input Validation Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
8. OWASP Cheat Sheet Series. *Server-Side Request Forgery Prevention Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
9. OWASP Cheat Sheet Series. *Error Handling Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html
10. OWASP Cheat Sheet Series. *Logging Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
11. OWASP Cheat Sheet Series. *Secrets Management Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
12. OWASP Cheat Sheet Series. *Transport Layer Security Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html
13. OWASP Cheat Sheet Series. *Password Storage Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
14. OWASP Foundation. *Application Security Verification Standard (ASVS).* The project page lists 5.0.0 as the latest version but labels its stability inconsistently; 4.0.3 (2021) is the previous stable release. https://owasp.org/www-project-application-security-verification-standard/

### 1.2 NIST

15. Chandramouli, R. and Butcher, Z. (NIST). *SP 800-228, Guidelines for API Protection for Cloud-Native Systems.* Original June 2025; updated final version 13 March 2026, which supersedes the original. https://csrc.nist.gov/pubs/sp/800/228/upd1/final
16. NIST. *SP 800-52 Rev. 2, Guidelines for the Selection, Configuration, and Use of TLS Implementations.* August 2019 (NIST lists it as under review). https://csrc.nist.gov/pubs/sp/800/52/r2/final
17. NIST. *SP 800-63B-4, Digital Identity Guidelines: Authentication.* SP 800-63-4 series, 2025. https://pages.nist.gov/800-63-4/sp800-63b.html

---

## 2. IETF RFCs

18. IETF. *RFC 5829: Link Relation Types for Simple Version Navigation between Web Resources.* April 2010. (Defines `successor-version`.) https://www.rfc-editor.org/rfc/rfc5829
19. IETF. *RFC 6585: Additional HTTP Status Codes.* (Defines 429 Too Many Requests.) https://www.rfc-editor.org/rfc/rfc6585
20. IETF. *RFC 6750: The OAuth 2.0 Authorization Framework: Bearer Token Usage.* https://www.rfc-editor.org/rfc/rfc6750
21. IETF. *RFC 8446: The Transport Layer Security (TLS) Protocol Version 1.3.* https://www.rfc-editor.org/rfc/rfc8446
22. IETF. *RFC 8594: The Sunset HTTP Header Field.* https://www.rfc-editor.org/rfc/rfc8594
23. IETF. *RFC 8725: JSON Web Token Best Current Practices.* https://www.rfc-editor.org/rfc/rfc8725
24. IETF. *RFC 9110: HTTP Semantics.* https://www.rfc-editor.org/rfc/rfc9110
25. IETF. *RFC 9457: Problem Details for HTTP APIs.* https://www.rfc-editor.org/rfc/rfc9457
26. Dalal, S. and Wilde, E. (IETF). *RFC 9745: The Deprecation HTTP Response Header Field.* March 2025. https://www.rfc-editor.org/rfc/rfc9745

---

## 3. Real-world incident sources

Background only. These incidents are described as reported by the sources, in date order of the incident. Where a source reports an attacker's claim or a regulator's allegation, it is described that way and not as established fact.

27. The Hacker News. *USPS Data Breach* (USPS Informed Visibility API flaw, up to 60 million accounts). 22 November 2018. https://thehackernews.com/2018/11/usps-data-breach.html
28. The New Stack. *How Parler's Data Was Harvested* (sequential post IDs, no authentication or rate limiting reported). January 2021. https://thenewstack.io/how-parlers-data-was-harvested/
29. TechCrunch. *Peloton's leaky API let anyone grab riders' private account data.* 5 May 2021. https://techcrunch.com/2021/05/05/peloton-bug-account-data-leak/
30. CSO Online. *Optus breach occurred due to a coding error, alleges ACMA* (an allegation, which Optus disputes). https://www.csoonline.com/article/2492520/optus-breach-occurred-due-to-a-coding-error-alleges-acma.html
31. T-Mobile US, Inc. *Form 8-K* (API incident, about 37 million accounts). Filed with the US SEC, 19 January 2023. https://www.sec.gov/Archives/edgar/data/1283699/000119312523010949/d641142d8k.htm
32. Help Net Security. *Data of 15 million Trello users scraped and offered for sale.* 23 January 2024. https://www.helpnetsecurity.com/2024/01/23/trello-users-data-scraped/
33. BleepingComputer. *Dell API abused to steal 49 million customer records in data breach* (largely the attacker's claims). 10 May 2024. https://www.bleepingcomputer.com/news/security/dell-api-abused-to-steal-49-million-customer-records-in-data-breach/

---

## 4. Tools used for the demo

34. Pallets Projects. *Flask documentation.* https://flask.palletsprojects.com/
35. Pallets Projects. *Werkzeug documentation* (password hashing helpers). https://werkzeug.palletsprojects.com/
36. Pallets Projects. *ItsDangerous documentation* (signed, timed tokens). https://itsdangerous.palletsprojects.com/
