"""Read-only MailMind inbox triage UI. No send/delete/archive actions."""
import os
import streamlit as st
from dotenv import load_dotenv

from email_reader import read_unread_emails
from ai_logic import generate_reply
from email_classifier import classify_email

load_dotenv()
st.set_page_config(page_title="MailMind | Live Inbox", page_icon="✉️", layout="wide")
st.title("MailMind · Live Inbox")
st.caption("Unrestricted sender inbox · Read-only Gmail · Drafts are never sent from this page.")

st.info("MailMind reads unread messages from **all senders**. It does not send, delete, archive, or mark emails as read")
username = os.getenv("GMAIL_USERNAME", "").strip()
password = os.getenv("GMAIL_APP_PASSWORD", "").strip()
if not username or not password:
    st.error("Set GMAIL_USERNAME and GMAIL_APP_PASSWORD in your local .env before connecting.")
    st.stop()

with st.sidebar:
    st.header("Inbox controls")
    limit = st.slider("Emails per refresh", min_value=1, max_value=25, value=10)
    st.caption("No sender allowlist. All unread senders are eligible.")
    st.caption("Messages are fetched with IMAP read-only mode and BODY.PEEK.")

if st.button("Refresh unread inbox", type="primary"):
    try:
        with st.spinner("Reading unread messages from all senders..."):
            st.session_state["live_emails"] = read_unread_emails(username, password, limit=limit)
            st.session_state.pop("live_error", None)
    except Exception as exc:
        st.session_state["live_error"] = f"Inbox connection failed: {exc}"

if st.session_state.get("live_error"):
    st.error(st.session_state["live_error"])

emails = st.session_state.get("live_emails", [])
if emails:
    st.success(f"Loaded {len(emails)} unread email(s) from any sender.")
    for idx, item in enumerate(emails):
        triage = classify_email(item["sender"], item["subject"], item["body"])
        label = f"{idx + 1}. [{triage['priority']}] {item['subject'] or '(no subject)'} · {item['sender']}"
        with st.expander(label, expanded=(idx == 0)):
            st.markdown("**From**")
            st.write(item["sender"])
            st.markdown("**Subject**")
            st.write(item["subject"])
            cols = st.columns(3)
            cols[0].metric("Category", triage["category"])
            cols[1].metric("Priority", triage["priority"])
            cols[2].metric("Automated", "Likely" if triage["automated"] else "Unlikely")
            st.caption(triage["reason"])
            st.markdown("**Suggested next step**")
            st.write(triage["suggested_action"])
            st.markdown("**Email body**")
            st.text_area("Original message", value=item["body"], height=170, disabled=True, key=f"live_body_{idx}")
            draft_key = f"live_draft_{idx}"
            if st.button("Generate reply draft", key=f"live_generate_{idx}"):
                context = f"From: {item['sender']}\nSubject: {item['subject']}\nCategory: {triage['category']}\n\nEmail body:\n{item['body']}"
                try:
                    draft, provider, warning = generate_reply(context, return_provider=True)
                    st.session_state[draft_key] = draft
                    st.session_state[f"live_provider_{idx}"] = provider
                    st.session_state[f"live_warning_{idx}"] = warning
                except Exception:
                    st.session_state[f"live_error_{idx}"] = "Draft generation failed. Try again later."
            if st.session_state.get(draft_key):
                st.markdown("**Editable reply draft**")
                st.text_area("Review and edit before copying", key=draft_key, height=190)
                provider = st.session_state.get(f"live_provider_{idx}", "rules")
                st.caption("Draft provider: " + ("Gemini" if provider == "gemini" else "Rules fallback"))
                warning = st.session_state.get(f"live_warning_{idx}")
                if warning:
                    st.warning("Gemini is unavailable, so MailMind used its local fallback draft.")
                if st.button("Clear draft", key=f"live_clear_{idx}"):
                    st.session_state.pop(draft_key, None)
                    st.rerun()
            if st.session_state.get(f"live_error_{idx}"):
                st.error(st.session_state[f"live_error_{idx}"])
elif "live_emails" in st.session_state:
    st.info("No unread emails found. Send an email to the connected mailbox or check Gmail's Inbox/Spam folders.")

st.divider()
st.caption("MailMind triage · Experimental prototype · No email actions are executed automatically.")
