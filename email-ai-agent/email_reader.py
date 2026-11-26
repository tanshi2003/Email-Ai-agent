"""Read the newest unread Gmail message and decode its plain-text body."""
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
                charset = part.get_content_charset() or "utf-8"
                candidates.append(payload.decode(charset, errors="replace"))
    else:
        payload = msg.get_payload(decode=True)
        if payload is not None:
            charset = msg.get_content_charset() or "utf-8"
            candidates.append(payload.decode(charset, errors="replace"))
    return "\n".join(candidates).strip()


def read_latest_email(username, password):
    """Returns (sender_address, subject, body, message_id); returns Nones when no mail."""
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        mail.login(username, password)
        mail.select("inbox")
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK" or not messages or not messages[0].strip():
            return None, None, None, None
        latest_id = messages[0].split()[-1]
        status, data = mail.fetch(latest_id, "(BODY.PEEK[])")
        if status != "OK" or not data or not isinstance(data[0], tuple):
            return None, None, None, None
        msg = email.message_from_bytes(data[0][1])
        sender_address = parseaddr(msg.get("From", ""))[1]
        subject = _decode_header_value(msg.get("Subject", ""))
        body = _plain_body(msg)
        message_id = (msg.get("Message-ID") or "").strip()
        return sender_address, subject, body, message_id
    finally:
        try:
            mail.logout()
        except Exception:
            pass
