"""Experimental Gmail inbox agent with duplicate checks and explicit console approval.

Use a dedicated test mailbox only. This script never sends automatically.
"""
import os
import re
import sqlite3
import time
from pathlib import Path

from dotenv import load_dotenv
from ai_logic import generate_reply
from email_reader import read_latest_email
from email_sender import send_email

load_dotenv()

USERNAME = os.getenv("GMAIL_USERNAME", "").strip()
PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()
POLL_INTERVAL = max(int(os.getenv("POLL_INTERVAL_SECONDS", "60")), 10)
ALLOWLIST = {s.strip().lower() for s in os.getenv("ALLOWED_SENDERS", "").split(",") if s.strip()}
DB_PATH = Path(__file__).resolve().parent.parent / "processed_messages.sqlite3"
AUTO_SEND_BLOCKED = {"no-reply", "noreply", "do-not-reply", "mailer-daemon", "postmaster"}


def _is_safe_sender(address):
    address = (address or "").strip().lower()
    if not address or any(token in address for token in AUTO_SEND_BLOCKED):
        return False
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", address))


def _db():
    connection = sqlite3.connect(DB_PATH)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS messages (message_id TEXT PRIMARY KEY, sender TEXT, subject TEXT, status TEXT, processed_at TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    return connection


def main():
    if not USERNAME or not PASSWORD:
        raise SystemExit("Set GMAIL_USERNAME and GMAIL_APP_PASSWORD in .env first.")
    print("MailMind live agent is experimental. Only use a dedicated test mailbox.")
    print("Drafts require manual approval. Ctrl+C stops the agent.")
    while True:
        try:
            sender, subject, body, message_id = read_latest_email(USERNAME, PASSWORD)
            if not sender:
                print("No unread email found.")
            elif not message_id:
                print("Skipping message without a Message-ID. Dedupe safety cannot be guaranteed.")
            elif not _is_safe_sender(sender):
                print(f"Skipped unsafe/automated sender: {sender}")
            elif ALLOWLIST and sender.lower() not in ALLOWLIST:
                print(f"Skipped sender not in ALLOWLIST: {sender}")
            else:
                with _db() as db:
                    already_seen = db.execute("SELECT status FROM messages WHERE message_id=?", (message_id,)).fetchone()
                    if already_seen:
                        print(f"Skipped duplicate Message-ID (status={already_seen[0]}).")
                    else:
                        draft = generate_reply(f"Subject: {subject or ''}\n\n{body or ''}")
                        db.execute("INSERT INTO messages(message_id,sender,subject,status) VALUES(?,?,?,?)", (message_id,sender,subject or "", "pending"))
                        print("\n" + "="*65)
                        print(f"FROM: {sender}\nSUBJECT: {subject}\n\nDRAFT:\n{draft}")
                        choice = input("\nSend this draft? [y]es / [n]o / [q]uit: ").strip().lower()
                        if choice == "y":
                            send_email(USERNAME, PASSWORD, sender, subject or "", draft)
                            db.execute("UPDATE messages SET status='sent' WHERE message_id=?", (message_id,))
                            print("Sent and marked as sent.")
                        elif choice == "n":
                            db.execute("UPDATE messages SET status='rejected' WHERE message_id=?", (message_id,))
                            print("Draft rejected and recorded. It will not be processed again.")
                        else:
                            db.execute("UPDATE messages SET status='pending' WHERE message_id=?", (message_id,))
                            print("Pending message recorded. Exiting.")
                            return
        except KeyboardInterrupt:
            print("\nAgent stopped.")
            break
        except Exception as exc:
            print(f"Agent cycle error: {exc}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
