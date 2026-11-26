# Email AI Agent

A Python-based email automation project that connects to a Gmail inbox, reads unread messages, generates a reply, and sends it through SMTP.

> **AI mode:** configure `GEMINI_API_KEY` to enable LLM-generated reply drafts through the Gemini API. Without a key, the agent falls back to the original deterministic keyword-based reply rules. The AI provider is isolated in `ai_logic.py`.

## What it does

- Connects to Gmail over IMAP SSL.
- Finds unread messages and extracts sender, subject, and plain-text content.
- Handles common email character encodings.
- Generates a reply using Gemini when configured, with a rule-based fallback.
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
- Streamlit for the local interactive sample-data demo
- Gemini API (optional, via an environment key)

## Repository structure

```text
.
├── email-ai-agent/
│   ├── ai_logic.py
│   ├── email_agent.py
│   ├── demo.py
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
4. Set `GMAIL_USERNAME` and `GMAIL_APP_PASSWORD` in `.env` if you plan to connect your test mailbox.
5. Optionally set `GEMINI_API_KEY` to enable Gemini-generated drafts. You can keep `REPLY_PROVIDER=auto`.

Never use your normal Google password. Never commit `.env` or share an App Password.

### 5. Run the local interactive demo (sample data only)

```bash
streamlit run email-ai-agent/demo.py
```

The demo never connects to Gmail or sends email. Try the sample messages to preview generated drafts. Configure `GEMINI_API_KEY` in your environment to use the Gemini provider.

### 6. Start the live inbox agent

From the repository root:

```bash
python email-ai-agent/email_agent.py
```

Stop it with Ctrl+C.

## Safety before connecting a real inbox

The live inbox script still sends replies automatically. Test with a dedicated mailbox and controlled test messages first. Do not point it at a personal or work inbox until you have added sender allowlisting, duplicate-message protection, a review/approval step, robust MIME handling, and clear logging. Avoid replying to mailing lists, automated notifications, and messages where the sender address cannot be safely parsed.

If an App Password was ever committed to this repository, revoke it in Google Account security and create a new one. Removing it from the latest source does not erase it from Git history.

## Current limitations and roadmap

- [ ] Add a draft-only mode and explicit send approval.
- [ ] Add message-ID based deduplication so polling cannot send repeated replies.
- [ ] Add sender allowlists and skip automated/no-reply messages.
- [ ] Add unit tests for decoding, classification, and reply generation.
- [x] Add a Gemini-backed response provider with configurable model, prompt, request timeout, and rule-based fallback.
- [ ] Add structured logs and clearer error handling.
- [x] Add a local Streamlit demo using sample emails, with no access to a real inbox.

## Demo

Run `streamlit run email-ai-agent/demo.py` to open the local interactive showcase. It uses fictional sample emails only and never reads an inbox or sends a message.

## Author

**Tanshi Khandelwal**  
[GitHub](https://github.com/tanshi2003)
