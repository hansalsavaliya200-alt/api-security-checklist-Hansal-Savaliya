# API Security Checklist (REST / Web APIs)

RedKross Research Foundation internship task, **Intern ID 2424**.

**Explanatory video:** [Add your YouTube (unlisted) or Google Drive link here]

## Objective
Develop a defensive checklist for REST/web APIs covering authentication, object-level authorisation, input validation, rate limiting, error handling, transport security, secrets, logging, and version/deprecation management, with a simple example of safe request/response design and references.

The demo also includes a small health endpoint and authenticated user/profile endpoints to make the local API easier to exercise and extend for further testing or UI integration. The health endpoint reports uptime, note listing supports `limit` and `offset` pagination, and responses expose rate-limit metadata headers. The browser UI at `http://127.0.0.1:5000/` (or `/ui`) supports login, note creation/edit/deletion, a seven-day activity chart, live API metrics, and a persistent light/dark theme preference. Its bearer token remains in memory only and is cleared on page reload.

All examples use a **local demo with fictional data**. Nothing here targets a real system.

## Deliverables
| Deliverable | Location |
|---|---|
| API security checklist | [`checklist/api-security-checklist.md`](checklist/api-security-checklist.md) |
| Safe request/response examples | [`demo/safe-request-response-examples.md`](demo/safe-request-response-examples.md) |
| Demo API (Flask) and tests | [`demo/`](demo/) |
| Technical report (Markdown) | [`report/technical-report.md`](report/technical-report.md) |
| Technical report (PDF) | [`report/technical-report.pdf`](report/technical-report.pdf) |
| Research notes (sources checked, incidents) | [`report/research-notes.md`](report/research-notes.md) |
| References | [`references.md`](references.md) |
| Screenshots / captured output | [`screenshots/`](screenshots/) |

## Approach
1. Researched OWASP API Security Top 10 (2023), OWASP cheat sheets, NIST SP 800-228 and relevant RFCs.
2. Turned the guidance into numbered, testable checklist items (priority + how to verify).
3. Built a small Flask API (fictional users/notes) that demonstrates the controls.
4. Added 24 automated tests and a `curl` walkthrough to exercise the API controls and frontend routes.
5. Documented limitations honestly in the report.

## Repository structure
```
.
├── README.md
├── references.md
├── checklist/
│   └── api-security-checklist.md
├── demo/
│   ├── app.py                         # demo API (localhost only)
│   ├── test_app.py                    # automated tests
│   ├── start_demo.bat                 # Windows one-command server + browser launcher
│   ├── run_demo.sh                    # curl walkthrough
│   ├── static/                        # browser UI assets
│   ├── safe-request-response-examples.md
│   ├── requirements.txt
│   └── .env.example                   # fake placeholder only
├── report/
│   ├── technical-report.pdf
│   ├── technical-report.md
│   └── research-notes.md
└── screenshots/
    ├── demo_run_output.txt
    └── test-results.txt
```

## Running the demo (local only)
Requirements: Python 3.10+ and curl.

### Windows: start frontend and backend with one command

Open PowerShell in the `demo` folder and run:

```powershell
.\start_demo.bat
```

The script starts Flask in that terminal and opens the frontend at `http://127.0.0.1:5000/` when the server is ready. If the demo is already running, it opens the existing UI instead of starting a second server. Press **Ctrl+C** in the terminal to stop the server. If dependencies are not installed yet, create the virtual environment and install them first:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The frontend is served by Flask, so there is no separate frontend server to start.

### macOS/Linux: manual startup

```bash
cd demo
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# optional: set your own signing key (otherwise a random one is generated at start-up)
export DEMO_SECRET_KEY="$(python -c 'import secrets;print(secrets.token_urlsafe(32))')"

python app.py                      # serves http://127.0.0.1:5000
```

In a second terminal:
```bash
./run_demo.sh                      # on Windows use Git Bash or WSL
```

Run the tests (no server needed):
```bash
python -m unittest -v test_app.py
```

Fictional demo accounts: `alice` / `demo-password-alice` and `bob` / `demo-password-bob`.

## Safety notes
- The server binds to `127.0.0.1` only and has debug mode off. Do not expose it to a network.
- All accounts and data are fictional. No real secrets are stored in this repository.
- Security testing was done only against this local demo.

## Limitations
In-memory storage and rate limiting, plain HTTP on localhost (TLS is described in the checklist but not demonstrated), and no token revocation/MFA/roles. See section 9 of the report.

## Author
Hansal Savaliya, Intern ID 2424
