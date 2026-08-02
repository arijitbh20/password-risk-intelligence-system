# Password Risk Intelligence System

Most password strength checkers are pretty shallow — they check length, maybe throw in a "contains a number" rule, and call it a day. I wanted something that actually reflects how passwords fail in the real world, so this project combines entropy math, a rule-based scoring engine, and live breach data from Have I Been Pwned, then logs everything for analysis on a dashboard.

It's not meant to be a production-grade security product. Think of it as a serious take on a common beginner project, built with the kind of architecture (FastAPI backend, Streamlit frontend, separate analytics layer) you'd actually want if this were real.

## What it does

**Entropy analysis** — I calculate entropy as `Length × log2(CharacterPoolSize)`, where the pool size depends on what character types actually show up in the password (lowercase, uppercase, digits, special chars). Anything above 128 bits gets capped, since the raw math starts producing numbers that don't mean much in practice.

**Rule-based scoring** — A custom rule engine scores passwords from 0 (very weak) to 8 (excellent) based on length, character diversity, repeated characters, common patterns, keyboard sequences (things like `qwerty` or `asdf123`), and a small bonus for passphrase-style formatting.

**Breach intelligence** — This is the part I think matters most. A password can look "strong" by every rule-based metric and still be garbage if it's been leaked a million times. The system checks against HIBP using the k-anonymity model — it hashes the password locally with SHA-1 and only sends the first 5 characters of that hash to the API. The plaintext password never leaves the app, and HIBP has no way to reconstruct it from what it receives.

**Risk classification** — Based on breach count, entropy, and rule score, each password gets classified as LOW, MEDIUM, HIGH, or CRITICAL. Breach count is weighted the heaviest here — a leaked password is dangerous no matter how "complex" it looks on paper.

**Logging and analytics** — Every check gets logged to SQLite (timestamp, risk status, breach count, score, entropy — never the password itself), and a separate Streamlit dashboard visualizes risk distribution, daily trends, score distributions, and correlations between the metrics. It auto-refreshes every 3.5 seconds.

## How it's put together

```
project/
│
├── app.py                     # FastAPI backend
├── frontend_app.py            # User-facing input UI
├── dashboard_app.py           # Analytics dashboard
├── Database.py                # SQLite read/write logic
├── ComputeMetrics.py          # Entropy, scoring, breach-check logic
│
├── database/
│   └── password.db
│
└── requirements.txt
```

The backend is a single FastAPI service exposing `POST /api/check-password`, which does the actual entropy/rule/breach computation and returns a risk classification. The frontend just talks to that endpoint. The dashboard is intentionally kept separate so it can be deployed or scaled independently of the checker itself.

## Stack

- **Backend:** Python, FastAPI, Pydantic
- **Frontend:** Streamlit
- **Storage:** SQLite
- **Analytics:** Pandas, Plotly
- **Security/networking:** Requests, SHA-1 hashing, HIBP API

## Running it locally

Clone the repo and install dependencies:

```bash
git clone <repository-url>
cd project
pip install -r requirements.txt
```

Then start each piece in its own terminal.

**1. Backend**
```bash
uvicorn app:app --reload
```
Runs at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

**2. Frontend**
```bash
streamlit run frontend_app.py
```
`http://localhost:8501`

**3. Analytics dashboard**
```bash
streamlit run dashboard_app.py --server.port 8502
```
`http://localhost:8502`

## Security notes

A few things I was deliberate about:

- Passwords are never stored or logged, anywhere, in any form.
- Nothing sent to a third party is reversible into the original password — only a 5-character SHA-1 hash prefix goes to HIBP.
- All database queries are parameterized, so there's no SQL injection surface from the logging layer.
- Network calls to HIBP are wrapped in timeout and exception handling — if the breach API is down or slow, the app degrades gracefully instead of failing the whole request.

## What I'd add next

- Swap the rule-based risk classifier for something ML-based, trained on labeled password risk data
- Basic auth in front of the dashboard (right now anyone with the URL can view it)
- Actual cloud deployment instead of local-only
- Exportable historical reports
- Role-based access if this ever needed multiple admins

## Why I built this

Mostly to get hands-on with FastAPI + Streamlit talking to each other, practice designing a small but real security workflow (k-anonymity isn't something you stumble into by accident), and get more comfortable with SQLite and Plotly for the analytics side. It touches backend API design, basic threat intelligence integration, and data viz in one project, which is why I picked it over a plainer CRUD app.
