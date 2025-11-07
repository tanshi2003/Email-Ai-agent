import imaplib
import email
from email.header import decode_header

def read_latest_email(username, password):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")

    # Search for all unread messages
    status, messages = mail.search(None, 'UNSEEN')
    messages = messages[0].split()

    if not messages:
        return None, None, None

    latest_email_id = messages[-1]
    status, data = mail.fetch(latest_email_id, "(RFC822)")
    raw_email = data[0][1]
    msg = email.message_from_bytes(raw_email)

    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else "utf-8")

    from_ = msg.get("From")

    # Extract email body
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    # Try to get the charset from the message part
                    charset = part.get_content_charset() or 'utf-8'
                    payload = part.get_payload(decode=True)
                    # Try different encodings if the first attempt fails
                    for encoding in [charset, 'utf-8', 'iso-8859-1', 'cp1252']:
                        try:
                            decoded_text = payload.decode(encoding)
                            body += decoded_text
                            break
                        except UnicodeDecodeError:
                            continue
                    else:  # If no encoding worked
                        body += payload.decode('utf-8', errors='replace')
                except Exception as e:
                    print(f"Error decoding email part: {str(e)}")
                    continue
    else:
        try:
            charset = msg.get_content_charset() or 'utf-8'
            payload = msg.get_payload(decode=True)
            # Try different encodings if the first attempt fails
            for encoding in [charset, 'utf-8', 'iso-8859-1', 'cp1252']:
                try:
                    body = payload.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:  # If no encoding worked
                body = payload.decode('utf-8', errors='replace')
        except Exception as e:
            print(f"Error decoding email: {str(e)}")
            body = ""

    return from_, subject, body
