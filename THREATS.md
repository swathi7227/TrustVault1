\# TrustVault Security Threat Model



\## 1. Purpose



TrustVault is a secure document-sharing platform built with Python, FastAPI, and PostgreSQL. This threat model identifies key risks to document confidentiality, integrity, authentication, and auditability.



\## 2. Assets to Protect



\- User credentials and authentication tokens

\- Uploaded documents and document metadata

\- Document ownership and access permissions

\- Database records

\- Audit logs and security events

\- Application secrets and database credentials



\## 3. Threats and Mitigations



\### T1: Unauthorized Document Access



\*\*Threat:\*\* A user accesses another user's document without permission by changing a document ID or directly calling an API endpoint.



\*\*Mitigation:\*\* Enforce server-side ownership and permission checks on every document operation. Never rely on frontend restrictions alone.



\*\*Verification:\*\* Test access attempts by authenticated users who do not own the document and have not been granted access.



\### T2: Broken Authentication



\*\*Threat:\*\* An attacker obtains or misuses credentials or authentication tokens to impersonate a user.



\*\*Mitigation:\*\* Hash passwords securely, validate authentication tokens, protect secret keys, and require authentication for protected endpoints.



\*\*Verification:\*\* Test invalid credentials, missing tokens, and invalid or expired tokens where expiration is configured.



\### T3: Excessive Permissions



\*\*Threat:\*\* A user receives editing or download capabilities beyond the access granted by the document owner.



\*\*Mitigation:\*\* Enforce explicit permissions on the server and apply the principle of least privilege.



\*\*Verification:\*\* Confirm that read-only users cannot perform operations that require edit or owner privileges.



\### T4: Permission Revocation Failure



\*\*Threat:\*\* A user continues accessing a document after their permission has been revoked.



\*\*Mitigation:\*\* Check current permissions for each protected request and ensure revocation updates the authoritative database state.



\*\*Verification:\*\* Grant access, verify it works, revoke access, and verify subsequent requests are denied.



\### T5: Malicious or Unsafe File Uploads



\*\*Threat:\*\* An attacker uploads an oversized, unexpected, or malicious file.



\*\*Mitigation:\*\* Apply file-size limits, validate file types, generate server-side filenames, and store uploads outside publicly accessible directories.



\*\*Verification:\*\* Test unsupported file types, oversized files, and filename manipulation.



\### T6: Path Traversal



\*\*Threat:\*\* An attacker manipulates filenames or paths to access files outside the intended storage directory.



\*\*Mitigation:\*\* Never use an untrusted filename directly as a filesystem path. Generate storage identifiers on the server and constrain file operations to the intended storage location.



\*\*Verification:\*\* Test filenames containing path traversal patterns and verify that unrelated files cannot be accessed.



\### T7: Sensitive Information Exposure



\*\*Threat:\*\* Secrets, credentials, tokens, or private documents are exposed through source control, error messages, or logs.



\*\*Mitigation:\*\* Exclude `.env` and private storage from Git, use environment variables for secrets, and avoid logging credentials or document contents.



\*\*Verification:\*\* Inspect tracked files and logs for sensitive information before submission.



\### T8: SQL Injection



\*\*Threat:\*\* Malicious input manipulates database queries.



\*\*Mitigation:\*\* Use SQLAlchemy's parameterized query mechanisms and avoid constructing SQL statements through unsafe string concatenation.



\*\*Verification:\*\* Test suspicious input and confirm it is handled as data rather than executable SQL.



\### T9: Insufficient Auditability



\*\*Threat:\*\* Security-relevant document actions cannot be traced, or audit records are incomplete.



\*\*Mitigation:\*\* Record relevant events such as uploads, downloads, permission changes, and denied access attempts where required. Protect audit records against unauthorized modification.



\*\*Verification:\*\* Confirm that expected actions produce accurate audit events without recording secrets.



\### T10: Denial of Service



\*\*Threat:\*\* Repeated requests or oversized uploads exhaust application or storage resources.



\*\*Mitigation:\*\* Apply reasonable request and upload limits, enforce file-size restrictions, and consider rate limiting.



\*\*Verification:\*\* Test configured limits and confirm that rejected requests do not leave partial or inconsistent records.



\## 4. Security Assumptions



\- The application server and database are operated in a controlled environment.

\- Secrets are supplied through local environment configuration and are not committed to source control.

\- All document access is mediated by server-side authorization checks.

\- Production deployment requires appropriate HTTPS, secret management, monitoring, and backup practices.



\## 5. Residual Risks



A threat model does not prove that the application is secure. Each mitigation must be checked against the implementation and supported by automated tests or documented manual verification.



\## 6. Review Status



This document identifies intended protections and verification activities. Mark a threat as mitigated only after the relevant implementation and tests have been reviewed.



