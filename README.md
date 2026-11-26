# MailMind | Email AI Agent

A Python email assistant prototype that reads inbox messages over Gmail IMAP, generates reply drafts using Gemini (optional), and uses deterministic rule-based fallback.

> **Safety note:** The live inbox script is currently a prototype and sends automatically. Do not run it against a personal or work inbox. Use a dedicated test account only.

## Features

- Gmail inbox reading over IMAP SSL
- Reply drafting with optional Gemini API
- Configurable model and request timeout
- Rule-based fallback draft generation
- Sample-only Streamlit showcase that never connects to Gmail or sends
- Environment-based credentials

## Workflow

```text
Sample demo: sample email -> draft -> preview (never sends)
Live agent (prototype): IMAP -> generate reply -> SMTP send
```

## Repository structure

```text
.
├── .github/workflows/jekyll-gh-pages.yml
├── email-ai-agent/
│   ├── ai_logic.py
│   ├── demo.py
│   ├── email_agent.py
│   ├── email_reader.py
│   └── email_sender.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── index.html
```

## Setup (Windows)

```powershell
git clone https://github.com/tanshi2003/Email-Ai-agent.git
cd Email-Ai-agent
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Add Gemini key/model and optional Gmail credentials in the local `.env` file. Never commit this file or an App Password.

## Run the local safe demo

```powershell
streamlit run email-ai-agent/demo.py
```

The demo uses sample email data only. It never connects to Gmail or sends messages.

## Gemini settings

- `REPLY_PROVIDER=auto`: use Gemini when configured, otherwise rule-based fallback.
- `REPLY_PROVIDER=gemini`: require Gemini and report API errors.
- `REPLY_PROVIDER=rules`: rule-based replies only.
- `GEMINI_MODEL`: model identifier used by the Gemini API.

## Live inbox prototype

The current live script reads unread messages and sends replies automatically. **Do not use it with a personal/work inbox.** Before real inbox use, implement sender allowlisting, duplicate-message protection, a draft approval step, safe MIME handling, and logging.

If an App Password was ever committed to repository history, revoke it in Google Account security and replace it. Removing it from the latest code does not remove it from Git history.

## Roadmap

- [ ] Approval gate before sending live replies
- [ ] Message-ID deduplication
- [ ] Sender allowlist and auto-mail filtering
- [ ] Unit tests
- [x] Gemini reply provider with prompt constraints
- [ ] Retry/backoff and graceful fallback for temporary API outages
- [x] Sample-data Streamlit demo

## Author

Tanshi Khandelwal · [GitHub](https://github.com/tanshi2003)
