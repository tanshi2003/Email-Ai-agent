from email_reader import read_latest_email
from email_sender import send_email
from ai_logic import generate_reply
import time

# Replace these with your Gmail info
USERNAME = "tanshikhandelwal03@gmail.com"
PASSWORD = "jppy aazv knfv svyn"

print("📬 Email AI Agent started...")

while True:
    from_email, subject, body = read_latest_email(USERNAME, PASSWORD)
    if from_email:
        print(f"📨 New email from: {from_email}")
        print(f"Subject: {subject}")

        reply = generate_reply(body + " " + subject)
        send_email(USERNAME, PASSWORD, from_email, subject, reply)
    else:
        print("No new emails. Checking again in 1 minute...")
    time.sleep(60)