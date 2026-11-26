"""Inbox monitoring entry point.

Credentials are read from environment variables. Never hard-code app passwords.
The current reply generator is rule-based; configure an LLM provider separately
before describing the project as LLM-powered.
"""
import os
import time

from dotenv import load_dotenv

from ai_logic import generate_reply
from email_reader import read_latest_email
from email_sender import send_email

load_dotenv()

USERNAME = os.getenv("GMAIL_USERNAME")
PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))


def main():
    if not USERNAME or not PASSWORD:
        raise SystemExit(
            "Missing credentials. Set GMAIL_USERNAME and GMAIL_APP_PASSWORD "
            "in your local .env file."
        )

    print("Email agent started. Press Ctrl+C to stop.")
    while True:
        try:
            from_email, subject, body = read_latest_email(USERNAME, PASSWORD)
            if from_email:
                print(f"New email from: {from_email}")
                print(f"Subject: {subject}")
                reply = generate_reply(f"{subject or ''}\n{body or ''}")
                send_email(USERNAME, PASSWORD, from_email, subject or "", reply)
            else:
                print("No unread email found.")
        except KeyboardInterrupt:
            print("\nEmail agent stopped.")
            break
        except Exception as exc:
            print(f"Agent cycle failed: {exc}")

        time.sleep(max(POLL_INTERVAL, 10))


if __name__ == "__main__":
    main()
