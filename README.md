# Email AI Agent

A Python-based email automation project that connects to a Gmail inbox, reads unread messages, generates a reply, and sends it through SMTP.

> **Current implementation note:** the reply generator in this repository is currently rule-based keyword matching. The project demonstrates an end-to-end email automation workflow, not an LLM integration yet. An LLM provider can be added as a separate, testable reply-generation backend.

## What it does

- Connects to Gmail over IMAP SSL.
- Finds unread messages and extracts sender, subject, and plain-text content.
- Handles common email character encodings.
- Generates a reply using a replaceable reply-generation module.
- Sends a response through SMTP SSL.
- Runs as a polling process with configurable interval.

## Architecture

```text
Gmail Inbox
    |
    | IMAP over TLS
    v
email_reader.py
    |  sender, subject, body
    v
ai_logic.py
    |  reply text
    v
email_sender.py
    | SMTP over TLS
    v
Recipient
```

## Technology

- Python 3
- IMAP / SMTP (Python standard library)
- python-dotenv for local environment configuration

## Repository structure

```text
.
├── email-ai-agent/
│   ├── ai_logic.py
│   ├── email_agent.py
│   ├── email_reader.py
│   └── email_sender.py
├── requirements.txt
├── .env.example
└── README.md
```

## Run locally

### 1. Clone and enter the project

```bash
git clone https://github.com/tanshi2003/Email-Ai-agent.git
cd Email-Ai-agent
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Gmail

1. Enable 2-Step Verification on the Google account used for testing.
2. Create a Google App Password.
3. Copy `.env.example` to `.env`.
4. Set `GMAIL_USERNAME` and `GMAIL_APP_PASSWORD` in `.env`.

Never use your normal Google password. Never commit `.env` or share an App Password.

### 5. Start the agent

From the repository root:

```bash
python email-ai-agent/email_agent.py
```

Stop it with Ctrl+C.

## Safety before connecting a real inbox

The current script sends replies automatically. Test with a dedicated mailbox and controlled test messages first. Do not point it at a personal or work inbox until you have added sender allowlisting, duplicate-message protection, a review/approval step, robust MIME handling, and clear logging. Avoid replying to mailing lists, automated notifications, and messages where the sender address cannot be safely parsed.

If an App Password was ever committed to this repository, revoke it in Google Account security and create a new one. Removing it from the latest source does not erase it from Git history.

## Current limitations and roadmap

- [ ] Add a draft-only mode and explicit send approval.
- [ ] Add message-ID based deduplication so polling cannot send repeated replies.
- [ ] Add sender allowlists and skip automated/no-reply messages.
- [ ] Add unit tests for decoding, classification, and reply generation.
- [ ] Add an LLM-backed response provider with configurable model, prompt, timeout, and safe fallback.
- [ ] Add structured logs and clearer error handling.
- [ ] Add a browser demo using sample emails, with no access to a real inbox.

## Demo

A safe browser demo should use sample email content and show the generated draft without sending email or requesting credentials. It can demonstrate the user experience without exposing mailbox data.

## Author

**Tanshi Khandelwal**  
[GitHub](https://github.com/tanshi2003)
