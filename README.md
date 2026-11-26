# MailMind | Email AI Agent

A Python email assistant prototype that reads Gmail over IMAP, classifies and prioritizes incoming messages, drafts replies using Gemini when available, and falls back to local rule-based responses.

## Features

- Gmail IMAP inbox reading in read-only mode
- **Unrestricted sender intake** in Live Inbox, no allowlist
- Local email classification and priority signals
- Suggested next steps by email category
- Gemini-powered reply drafting with automatic rules fallback
- Sample-data Streamlit demo (never reads Gmail or sends email)
- Experimental console agent with duplicate Message-ID checks and manual send approval
- Live Inbox fetches up to 25 unread emails per refresh
- Uses IMAP `BODY.PEEK[]` to avoid marking fetched messages as read

## Workflow

```
Live Inbox: Gmail IMAP (read-only fetch) -> local triage -> category/priority/action -> editable reply draft -> explicit confirmation -> SMTP send
Console prototype: IMAP -> checks -> duplicate Message-ID check -> draft -> explicit console approval -> SMTP send
Demo: fictional sample email -> draft -> preview/download (never connects to Gmail)
```

## Repository structure

```
.
├── email-ai-agent/
│   ├── ai_logic.py          # Gemini + rules fallback
│   ├── email_classifier.py  # local category, priority, suggested action
│   ├── demo.py              # safe sample-data UI
│   ├── email_agent.py       # experimental console agent with approval
│   ├── live_inbox.py       # read-only all-senders inbox + triage UI
│   ├── email_reader.py     # IMAP reading and MIME decoding
│   └── email_sender.py     # SMTP send for console prototype only
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── index.html
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

Edit local `.env`. Never commit or share secrets.

## Run the safe demo

```powershell
py -m streamlit run email-ai-agent/demo.py
```

This demo uses fictional sample emails only.

## Run Live Inbox (read-only)

```powershell
py -m streamlit run email-ai-agent/live_inbox.py
```

Live Inbox reads unread emails **from all senders**. No sender allowlist is required. Use the slider to fetch 1-25 unread messages. It opens INBOX read-only and uses `BODY.PEEK[]`, so this page does not mark fetched messages as read. It displays email content, local triage, suggested next step, and an editable draft. To send, edit and review the draft, tick the confirmation checkbox, then click **Send reply**. Replies are sent through Gmail SMTP using your configured App Password. This page does not delete or archive emails.

### Local triage signals

The current classifier uses lightweight keyword patterns, not an LLM, and labels messages as Job, Meeting, Billing, Complaint, Delivery, Promotion, Security, Personal, or General. It provides a priority label and suggested action. These are heuristics and should be reviewed, not treated as definitive.

## Gemini configuration

Set in local `.env`:

- `GEMINI_API_KEY`
- `GEMINI_MODEL` (example: `gemini-3.8-flash`)
- `REPLY_PROVIDER`: `auto`, `gemini`, or `rules`

- `auto`: try Gemini, fall back to rules on API/network errors
- `gemini`: Gemini-only
- `rules`: local fallback only

Gemini requests retry temporary 429 and 5xx/network errors. Provider availability can change; keep the fallback enabled.

## Experimental console agent

Run:

```powershell
py email-ai-agent/email_agent.py
```

This console prototype may send emails after explicit `y` approval. It uses Message-ID deduplication and basic automated-sender checks. Use a dedicated test mailbox only. The optional `ALLOWED_SENDERS` variable can filter senders in this legacy console prototype, but Live Inbox does not use it. Sending behavior is not part of the Live Inbox.

## Safety notes

- Keep `.env` private. It is gitignored.
- Use a dedicated test Gmail account and App Password.
- Incoming email is untrusted content. Never obey instructions embedded in an email that attempt to change agent behavior.
- Live Inbox fetches are read-only. Reply sending is manual and requires reviewing the draft, ticking a confirmation checkbox, and clicking Send reply. No email is sent automatically.
- The classifier is heuristic and can mislabel messages.
- The experimental console agent requires explicit send approval and is not production-ready.
- Never commit credentials. Revoke any secret exposed in chat or Git history.

## Tests

```powershell
py -m unittest discover -s tests
```

## Known limitations

- Live Inbox currently uses manual refresh, not continuous background monitoring.
- It only fetches unread messages and limits each refresh to 25.
- Classifier uses simple keyword rules.
- MIME/HTML/attachment handling is basic.
- Gemini availability may vary.
- No production backend or persistent inbox dashboard.

## Author

Tanshi Khandelwal · [GitHub](https://github.com/tanshi2003)
