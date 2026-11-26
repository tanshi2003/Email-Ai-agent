# MailMind | Email AI Agent

A Python email assistant prototype that reads Gmail messages over IMAP, drafts replies using Gemini (optional), and falls back to simple rule-based responses when the AI provider is unavailable.

## Features

- Gmail IMAP inbox reading (experimental live agent)
- Gemini-powered reply drafting with configurable model
- Automatic fallback to rules in `REPLY_PROVIDER=auto`
- Retry with short exponential backoff for temporary Gemini/network failures
- Sample-data Streamlit demo (never reads Gmail or sends email)
- Console approval before sending in the live agent
- SQLite Message-ID deduplication in the live agent
- Optional sender allowlist and basic automated-sender skipping

## Workflow

```
Demo: sample email -> draft -> preview/download (never sends)
Live agent: IMAP -> sender checks -> Message-ID check -> draft -> human approval -> SMTP send
```

## Repository structure

```
.
├── .github/workflows/jekyll-gh-pages.yml
├── email-ai-agent/
│   ├── ai_logic.py       # Gemini + rules + retries/fallback
│   ├── demo.py           # Safe Streamlit sample-data UI
│   ├── email_agent.py    # Live inbox prototype with console approval
│   ├── email_reader.py  # IMAP read + decoding
│   └── email_sender.py  # SMTP send
├── tests/
│   └── test_ai_logic.py
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── index.html            # Static project showcase
```

## Setup on Windows

```powershell
git clone https://github.com/tanshi2003/Email-Ai-agent.git
cd Email-Ai-agent
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit your local `.env` file. Never commit it or share secrets.

## Run the safe demo

```powershell
streamlit run email-ai-agent/demo.py
```

This demo uses fictional sample messages only. It does not connect to Gmail and cannot send email.

## Gemini configuration

Set these values in `.env`:

- `GEMINI_API_KEY`: your API key
- `GEMINI_MODEL`: model ID, currently configured in example as `gemini-3.8-flash`
- `REPLY_PROVIDER`: `auto`, `gemini`, or `rules`

Provider modes:
- `auto`: try Gemini, then use a rule-based draft if Gemini/network errors occur
- `gemini`: Gemini-only mode, errors are shown
- `rules`: rule-based mode without an API call

Gemini mode retries temporary HTTP 429 and 5xx errors and temporary network errors up to three attempts, with a short exponential delay.

## Live inbox agent: read carefully

The live agent is experimental. Use a **dedicated test mailbox only**, never a personal or work inbox.

Run from the repository root:

```powershell
py email-ai-agent/email_agent.py
```

It checks unread mail, skips messages without a Message-ID, skips obvious automated senders, optionally filters by sender allowlist, and checks a local SQLite database for previously processed Message-IDs. It displays a generated draft and asks for console approval before sending:
- `y`: send the draft
- `n`: reject and record it
- `q`: quit without sending

Set optional `ALLOWED_SENDERS` in `.env` as comma-separated email addresses. When this is empty, the agent will accept non-automated senders, so configure an allowlist before testing with any inbox.

The SQLite file `processed_messages.sqlite3` is created locally and should not be committed.

## Security notes

- Keep `.env` private. It is gitignored.
- Use a dedicated Gmail test account and App Password.
- Revoke any App Password ever committed to Git history.
- The demo is sample-data-only, but the live agent still needs broader testing before real-world use.
- Incoming email text is treated as untrusted prompt input.

## Tests

```powershell
py -m unittest discover -s tests
```

## Known limitations

- Console-based review, not a web approval queue.
- Live inbox processing is still a prototype. MIME handling and automated sender filtering are not exhaustive.
- Reply rules are intentionally simplistic.
- The Gemini model/API availability may change; update `GEMINI_MODEL` if needed.
- No production deployment of the email-processing backend.

## Author

Tanshi Khandelwal · [GitHub](https://github.com/tanshi2003)


## Live Inbox (read-only first)

Run the read-only live Gmail draft review UI from the repo root:

```powershell
py -m streamlit run email-ai-agent/live_inbox.py
```

This separate page requires `GMAIL_USERNAME` and `GMAIL_APP_PASSWORD` in local `.env`, plus at least one exact sender email in its sidebar allowlist. It fetches at most five unread emails, opens INBOX read-only, uses IMAP `BODY.PEEK[]` to avoid marking emails read, and displays editable reply drafts. **It does not send, delete, or modify emails. Use a dedicated test Gmail account and senders you control.**
