\# TrustVault — Secure Document Sharing Platform



TrustVault is a secure document-sharing platform built with Python, FastAPI, and PostgreSQL. It is designed to protect sensitive documents through authentication, server-side access control, permission management, and audit logging.



\## Features



\- \*\*Authentication:\*\* User registration, login, and JWT-based authentication.

\- \*\*Document management:\*\* Upload and list documents.

\- \*\*Access control:\*\* Enforce document ownership and access permissions on the server.

\- \*\*Permission management:\*\* Grant or revoke document access.

\- \*\*Secure downloads:\*\* Restrict document downloads to authorized users.

\- \*\*Audit logging:\*\* Record relevant document access and management activities.



\## Technology Stack



\- Python 3.12

\- FastAPI

\- PostgreSQL

\- SQLAlchemy

\- Alembic

\- JWT authentication

\- Pytest (for testing, if configured)



\## Project Structure



```text

trustvault/

├── backend/

│   └── app/

│       ├── auth/

│       ├── core/

│       ├── db/

│       ├── documents/

│       ├── models/

│       ├── schemas/

│       └── main.py

├── migrations/

├── alembic.ini

├── requirements.txt

├── README.md

├── THREATS.md

└── PROMPTS.md

```



\## Local Setup



1\. Install Python 3.12 and PostgreSQL.

2\. Clone this repository.

3\. Create and activate a virtual environment.

4\. Install the dependencies listed in `requirements.txt`.

5\. Configure the database connection and authentication settings in a local `.env` file.

6\. Apply database migrations.

7\. Start the FastAPI server.



Example commands for Windows PowerShell:



```powershell

py -3.12 -m venv .venv312

.\\.venv312\\Scripts\\Activate.ps1

pip install -r requirements.txt

```



Configure your local environment variables before starting the application. Never commit `.env`, passwords, JWT secrets, or private documents to GitHub.



Apply migrations and start the server using the commands configured for this project.



\## API Documentation



When the application is running locally, FastAPI's interactive API documentation is available at:



`http://127.0.0.1:8000/docs`



Use the actual port configured for your server if it differs.



\## Security Considerations



\- Enforce authorization checks on the server for every document operation.

\- Do not trust client-supplied document ownership or permission claims.

\- Store uploaded documents outside publicly accessible directories.

\- Keep secrets in environment variables.

\- Test unauthorized access, permission revocation, and document downloads.

\- Maintain audit records for security-relevant operations.



\## Challenge Documentation



\- `THREATS.md` — Security threats, risks, and mitigations.

\- `PROMPTS.md` — Documentation of AI assistance and relevant prompts, as required by the challenge.



\## Project Status



This project is being developed as part of a secure document-sharing platform hiring challenge. Features and security claims should be verified against the current implementation and test results.



