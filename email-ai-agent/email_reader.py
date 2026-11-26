"""Read unread Gmail messages over IMAP without marking them as read."""
import email
import imaplib
from email.header import decode_header
from email.utils import parseaddr


def _decode_header_value(value):
    parts = decode_header(value or "")
    decoded = []
    for part, encoding in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(encoding or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return "".join(decoded)


def _plain_body(msg):
    candidates = []
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() != "text/plain" or part.get_content_disposition() == "attachment":
                continue
            payload = part.get_payload(decode=True)
            if payload is not None:
                candidates.append(payload.decode(part.get_content_charset() or "utf-8", errors="replace"))
    else:
        payload = msg.get_payload(decode=True)
        if payload is not None:
            candidates.append(payload.decode(msg.get_content_charset() or "utf-8", errors="replace"))
    return "\n".join(candidates).strip()


def read_latest_email(username, password):
    """Returns (sender, subject, body, message_id), or Nones when no unread email."""
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        mail.login(username, password)
        mail.select("INBOX", readonly=True)
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK" or not messages or not messages[0].strip():
            return None, None, None, None
        latest_id = messages[0].split()[-1]
        status, data = mail.fetch(latest_id, "(BODY.PEEK[])")
        if status != "OK" or not data or not isinstance(data[0], tuple):
            return None, None, None, None
        msg = email.message_from_bytes(data[0][1])
        return parseaddr(msg.get("From", ""))[1], _decode_header_value(msg.get("Subject", "")), _plain_body(msg), (msg.get("Message-ID") or "").strip()
    finally:
        try:
            mail.logout()
        except Exception:
            pass


def read_unread_emails(username, password, limit=10):
    """Return unread emails from all senders, newest first, in read-only mode."""
    if limit < 1 or limit > 25:
        raise ValueError("Inbox fetch limit must be between 1 and 25.")
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        mail.login(username, password)
        status, _ = mail.select("INBOX", readonly=True)
        if status != "OK":
            raise RuntimeError("Could not open Gmail inbox in read-only mode.")
        status, data = mail.search(None, "UNSEEN")
        if status != "OK" or not data or not data[0].strip():
            return []
        ids = data[0].split()[-limit:]
        results = []
        for uid in reversed(ids):
            status, parts = mail.fetch(uid, "(BODY.PEEK[])")
            if status != "OK" or not parts or not isinstance(parts[0], tuple):
                continue
            msg = email.message_from_bytes(parts[0][1])
            results.append({
                "sender": parseaddr(msg.get("From", ""))[1].strip(),
                "subject": _decode_header_value(msg.get("Subject", "")),
                "body": _plain_body(msg),
                "message_id": (msg.get("Message-ID") or "").strip(),
                "imap_id": uid.decode("ascii", errors="ignore"),
            })
        return results
    finally:
        try:
            mail.logout()
        except Exception:
            pass
