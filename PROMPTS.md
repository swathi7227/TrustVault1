\# PROMPTS.md — TrustVault



\## Purpose



This document records how AI assistance was used during the development of TrustVault. It supports transparency and documents the role of AI in the development process.



\## Areas Where AI Assistance Was Used



AI assistance was used to help with:



\- Understanding the project requirements and breaking the work into manageable steps.

\- Planning the FastAPI backend and project structure.

\- Understanding Python, FastAPI, SQLAlchemy, PostgreSQL, and Alembic.

\- Implementing and reviewing authentication and password-hashing concepts.

\- Designing document access controls and server-side authorization checks.

\- Troubleshooting development environment, database, and Git issues.

\- Drafting project documentation, including README.md and THREATS.md.

\- Identifying security risks and suggesting relevant tests.



\## Development Approach



AI-generated suggestions were reviewed and adapted during implementation. Commands and code were run locally where possible, and errors were investigated iteratively.



AI assistance does not replace verification. Security-sensitive behavior must be validated through code review and automated tests.



\## Verification and Limitations



The following should be verified before submission:



\- Authentication and token validation.

\- Document ownership and permission enforcement.

\- Unauthorized download and modification attempts.

\- Permission revocation.

\- Upload validation and storage-path safety.

\- Database migration behavior.

\- Automated test results.



Do not treat a feature as verified unless it has been tested successfully.



\## Responsible Use



The developer remains responsible for understanding, reviewing, testing, and explaining the submitted implementation. No secrets, passwords, access tokens, or private credentials should be included in this document.



\## Accuracy Note



This file describes the intended areas of AI assistance. Update it as needed so that it accurately reflects the tools used and the actual development process.



