"""Safe MailMind credential check: Gmail read-only login + one Gemini request.
Never prints credentials or reads message contents.
"""
import json
import os
import socket
import urllib.error
import urllib.request

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Missing python-dotenv. Run: py -m pip install python-dotenv")
    raise SystemExit(1)

print("=== MailMind credential verification ===")
gmail_user = os.getenv("GMAIL_USERNAME", "").strip()
gmail_pass = os.getenv("GMAIL_APP_PASSWORD", "").replace(" ", "").strip()
gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

# Gmail: authenticate and select INBOX read-only, without fetching emails.
print("\n[1/2] Gmail read-only authentication test")
if not gmail_user or not gmail_pass:
    print("FAIL: Gmail username or app password missing in .env")
else:
    try:
        import imaplib
        with imaplib.IMAP4_SSL("imap.gmail.com", timeout=20) as imap:
            imap.login(gmail_user, gmail_pass)
            status, _ = imap.select("INBOX", readonly=True)
            if status == "OK":
                print("PASS: Gmail login succeeded and INBOX opened read-only. No emails fetched.")
            else:
                print(f"FAIL: Login succeeded, but read-only INBOX selection returned {status}.")
            imap.logout()
    except Exception as exc:
        print(f"FAIL: Gmail authentication/connection error: {type(exc).__name__}: {exc}")

# Gemini: one tiny prompt, no retries, 60-second timeout.
print("\n[2/2] Gemini generation test")
if not gemini_key:
    print("FAIL: GEMINI_API_KEY missing in .env")
else:
    payload = {
        "contents": [{"parts": [{"text": "Reply with exactly: MailMind test OK"}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 20}
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"x-goog-api-key": gemini_key, "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read())
            out = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            print(f"PASS: Gemini responded HTTP {response.status} using model {model}.")
            print("Model response:", out.strip())
    except urllib.error.HTTPError as err:
        try:
            error_json = json.loads(err.read())
            info = error_json.get("error", {})
            print(f"FAIL: Gemini HTTP {err.code}: {info.get('status', '')} | {info.get('message', '')}")
        except Exception:
            print(f"FAIL: Gemini HTTP {err.code}")
    except (TimeoutError, socket.timeout) as exc:
        print(f"FAIL: Gemini request timed out after 60 seconds: {exc}")
    except Exception as exc:
        print(f"FAIL: Gemini connection error: {type(exc).__name__}: {exc}")

print("\nFinished. Credentials were not printed. No emails were fetched or sent.")
