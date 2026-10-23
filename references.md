# References

The source review date and research notes are documented in [`report/research-notes.md`](report/research-notes.md).

## Standards and guidance
1. OWASP Foundation. *OWASP API Security Top 10 – 2023.* https://owasp.org/API-Security/editions/2023/en/0x11-t10/
2. OWASP Cheat Sheet Series. *REST Security Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html
3. OWASP Cheat Sheet Series. *Authentication Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
4. OWASP Cheat Sheet Series. *Authorization Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
5. OWASP Cheat Sheet Series. *Input Validation Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
6. OWASP Cheat Sheet Series. *Error Handling Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html
7. OWASP Cheat Sheet Series. *Logging Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
8. OWASP Cheat Sheet Series. *Secrets Management Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
9. OWASP Cheat Sheet Series. *Transport Layer Security Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html
10. OWASP Cheat Sheet Series. *Password Storage Cheat Sheet.* https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
11. OWASP. *Application Security Verification Standard (ASVS).* https://owasp.org/www-project-application-security-verification-standard/
12. NIST. *SP 800-228, Guidelines for API Protection for Cloud-Native Systems* (original June 2025; updated final version of 13 March 2026, which supersedes the original). https://csrc.nist.gov/pubs/sp/800/228/upd1/final
13. NIST. *SP 800-52 Rev. 2, Guidelines for the Selection, Configuration, and Use of TLS Implementations* (August 2019; NIST lists it as under review). https://csrc.nist.gov/pubs/sp/800/52/r2/final
14. NIST. *SP 800-63B-4, Digital Identity Guidelines: Authentication* (SP 800-63-4 series, 2025). https://pages.nist.gov/800-63-4/sp800-63b.html

## IETF RFCs
15. RFC 6750. *The OAuth 2.0 Authorization Framework: Bearer Token Usage.* https://www.rfc-editor.org/rfc/rfc6750
16. RFC 8725. *JSON Web Token Best Current Practices.* https://www.rfc-editor.org/rfc/rfc8725
17. RFC 6585. *Additional HTTP Status Codes* (429 Too Many Requests). https://www.rfc-editor.org/rfc/rfc6585
18. RFC 9457. *Problem Details for HTTP APIs.* https://www.rfc-editor.org/rfc/rfc9457
19. RFC 8594. *The Sunset HTTP Header Field.* https://www.rfc-editor.org/rfc/rfc8594
20. RFC 9745. *The Deprecation HTTP Response Header Field.* https://www.rfc-editor.org/rfc/rfc9745
21. RFC 8446. *The Transport Layer Security (TLS) Protocol Version 1.3.* https://www.rfc-editor.org/rfc/rfc8446
22. RFC 9110. *HTTP Semantics.* https://www.rfc-editor.org/rfc/rfc9110

23. RFC 5829. *Link Relation Types for Simple Version Navigation between Web Resources* (defines `successor-version`). https://www.rfc-editor.org/rfc/rfc5829

## Real-world incident sources (background only; cite as reported)
24. T-Mobile US, Inc. *Form 8-K*, 19 January 2023. https://www.sec.gov/Archives/edgar/data/1283699/000119312523010949/d641142d8k.htm
25. TechCrunch. *Peloton's leaky API let anyone grab riders' private account data*, 5 May 2021. https://techcrunch.com/2021/05/05/peloton-bug-account-data-leak/
26. CSO Online. *Optus breach occurred due to a coding error, alleges ACMA* (an allegation; Optus disputes it). https://www.csoonline.com/article/2492520/optus-breach-occurred-due-to-a-coding-error-alleges-acma.html

## Tools used for the demo
27. Flask documentation. https://flask.palletsprojects.com/
28. Werkzeug security helpers (password hashing). https://werkzeug.palletsprojects.com/
29. ItsDangerous (signed, timed tokens). https://itsdangerous.palletsprojects.com/

*Note on ASVS (item 11): the OWASP project page lists 5.0.0 as the latest version but labels its stability inconsistently. State the exact version you consulted.*
