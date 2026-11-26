"""Read-only live Gmail draft review UI for MailMind. No sending capability."""
import os
import streamlit as st
from dotenv import load_dotenv

from email_reader import read_unread_emails
from ai_logic import generate_reply

load_dotenv()
st.set_page_config(page_title="MailMind | Live Inbox", page_icon="✉️", layout="wide")
st.title("MailMind · Live Inbox")
st.caption("Read-only inbox connection · Up to 5 unread messages · Drafts are never sent from this page.")

st.warning("Use a dedicated Gmail test mailbox. This page only reads email and generates editable drafts. It has no send action.")
username = os.getenv("GMAIL_USERNAME", "").strip()
password = os.getenv("GMAIL_APP_PASSWORD", "").strip()
if not username or not password:
    st.error("Set GMAIL_USERNAME and GMAIL_APP_PASSWORD in your local .env before connecting.")
    st.stop()

with st.sidebar:
    st.header("Safety settings")
    allowlist_raw = st.text_area("Approved sender addresses (comma-separated)", value=os.getenv("ALLOWED_SENDERS", ""), help="Required. Only exact sender addresses listed here are loaded.")
    allowlist = [a.strip().lower() for a in allowlist_raw.split(",") if a.strip()]
    st.caption("Exact-match allowlist is required. Inbox is opened read-only.")
    st.caption("Maximum fetch: 5 unread emails per refresh.")

if not allowlist:
    st.info("Add at least one approved sender email address in the sidebar, then refresh the inbox.")
    st.stop()

if st.button("Refresh unread inbox", type="primary"):
    try:
        with st.spinner("Connecting securely and reading approved unread messages..."):
            st.session_state["live_emails"] = read_unread_emails(username, password, allowlist, limit=5)
            st.session_state["live_allowlist"] = allowlist
            st.session_state.pop("live_error", None)
    except Exception as exc:
        st.session_state["live_error"] = f"Inbox connection failed: {exc}"

if st.session_state.get("live_error"):
    st.error(st.session_state["live_error"])
emails = [item for item in st.session_state.get("live_emails", []) if item["sender"].strip().lower() in set(allowlist)]
if emails:
    st.success(f"Loaded {len(emails)} approved unread email(s).")
    for idx, item in enumerate(emails):
        with st.expander(f"{idx + 1}. {item['subject'] or '(no subject)'} · {item['sender']}", expanded=(idx == 0)):
            st.markdown("**From**")
            st.write(item["sender"])
            st.markdown("**Subject**")
            st.write(item["subject"])
            st.markdown("**Email body**")
            st.text_area("Original message", value=item["body"], height=170, disabled=True, key=f"live_body_{idx}")
            draft_key = f"live_draft_{idx}"
            if st.button("Generate reply draft", key=f"live_generate_{idx}"):
                context = f"From: {item['sender']}\nSubject: {item['subject']}\n\n{item['body']}"
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
                if st.button("Clear draft", key=f"live_clear_{idx}"):
                    st.session_state.pop(draft_key, None)
                    st.rerun()
            if st.session_state.get(f"live_error_{idx}"):
                st.error(st.session_state[f"live_error_{idx}"])
else:
    if "live_emails" in st.session_state:
        st.info("No unread messages from the approved sender addresses were found.")

st.divider()
st.caption("MailMind live inbox · Read-only prototype · Nothing is sent or marked as read by this page.")
