"""MailMind polished Live Inbox UI. Read-only fetching with reviewed manual reply sending."""
import os
import streamlit as st
from dotenv import load_dotenv

from email_reader import read_unread_emails
from ai_logic import generate_reply
from email_classifier import classify_email
from email_sender import send_email

load_dotenv()
st.set_page_config(page_title="MailMind | Live Inbox", page_icon="📬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --mm-bg:#0b1017; --mm-card:#131b25; --mm-border:#273446; --mm-text:#edf2fa; --mm-muted:#91a0b4; --mm-accent:#aab9ff; }
html, body, [data-testid="stAppViewContainer"] { background:var(--mm-bg); color:var(--mm-text); font-family:'DM Sans',sans-serif; }
[data-testid="stHeader"] { background:transparent; }
.block-container { max-width:1440px; padding-top:2.2rem; padding-bottom:3rem; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; letter-spacing:-.03em; }
[data-testid="stSidebar"] { background:#101722; border-right:1px solid var(--mm-border); }
[data-testid="stSidebar"] * { color:#dbe4f1; }
div[data-testid="stExpander"] { background:var(--mm-card); border:1px solid var(--mm-border); border-radius:16px; margin-bottom:12px; }
div[data-testid="stExpander"] summary { font-weight:600; }
[data-testid="stMetric"] { background:#111923; border:1px solid var(--mm-border); padding:14px 16px; border-radius:14px; }
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input { background:#0f1620 !important; border:1px solid #344357 !important; border-radius:12px !important; color:#eaf0f8 !important; }
[data-testid="stButton"] button { border-radius:10px !important; border:1px solid #344357 !important; font-weight:600 !important; transition:all .15s ease; }
[data-testid="stButton"] button:hover { border-color:#aab9ff !important; color:#c5ceff !important; transform:translateY(-1px); }
[data-testid="stButton"] button[kind="primary"] { background:#aab9ff !important; color:#111827 !important; border:none !important; }
hr { border-color:#273446 !important; }
.mailmind-hero { background:linear-gradient(135deg,#182333,#111923 65%,#1d2938); border:1px solid #2a3a50; border-radius:22px; padding:24px 28px; margin-bottom:18px; }
.mailmind-eyebrow { color:#aab9ff; text-transform:uppercase; letter-spacing:.16em; font-size:12px; font-weight:800; margin-bottom:8px; }
.mailmind-title { font-family:Manrope,sans-serif; font-size:32px; font-weight:800; letter-spacing:-.04em; color:#f4f7fc; margin:0; }
.mailmind-sub { color:#9eacc0; margin-top:8px; font-size:14px; }
.mailmind-pill { display:inline-block; background:#202e41; border:1px solid #354a64; color:#c6d5ee; padding:5px 10px; border-radius:999px; font-size:12px; margin-right:6px; margin-top:12px; }
.mailmind-section { color:#aab9ff; font-size:12px; letter-spacing:.14em; font-weight:800; text-transform:uppercase; margin:4px 0 12px; }
.mailmind-note { background:#111a25; border:1px solid #263548; border-radius:12px; padding:12px 15px; color:#9cabc0; font-size:13px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="mailmind-hero">
  <div class="mailmind-eyebrow">MailMind · Personal email workspace</div>
  <p class="mailmind-title">Your inbox, with a little intelligence.</p>
  <div class="mailmind-sub">Triage unread mail, understand what matters, and draft thoughtful replies. Nothing is sent without your review.</div>
  <span class="mailmind-pill">Read-only inbox fetch</span><span class="mailmind-pill">AI-assisted drafts</span><span class="mailmind-pill">Manual send approval</span>
</div>
""", unsafe_allow_html=True)

username = os.getenv("GMAIL_USERNAME", "").strip()
password = os.getenv("GMAIL_APP_PASSWORD", "").strip()
if not username or not password:
    st.error("Set GMAIL_USERNAME and GMAIL_APP_PASSWORD in your local .env before connecting.")
    st.stop()

with st.sidebar:
    st.markdown("## Inbox settings")
    limit = st.slider("Emails per refresh", min_value=1, max_value=25, value=10)
    st.caption("All unread senders are eligible. MailMind fetches with IMAP read-only mode and BODY.PEEK.")
    st.markdown("---")
    st.markdown("### Privacy")
    st.markdown('<div class="mailmind-note">Fetching does not mark messages as read. Sending is always a separate, reviewed action.</div>', unsafe_allow_html=True)

col_refresh, col_info = st.columns([1, 3], vertical_alignment="center")
with col_refresh:
    refresh = st.button("↻  Refresh unread inbox", type="primary", use_container_width=True)
with col_info:
    st.caption("Refresh to load unread emails from your connected Gmail inbox.")

if refresh:
    try:
        with st.spinner("Connecting securely and fetching unread mail…"):
            st.session_state["live_emails"] = read_unread_emails(username, password, limit=limit)
            st.session_state.pop("live_error", None)
    except Exception as exc:
        st.session_state["live_error"] = f"Inbox connection failed: {exc}"

if st.session_state.get("live_error"):
    st.error(st.session_state["live_error"])

emails = st.session_state.get("live_emails", [])
if emails:
    st.markdown(f'<div class="mailmind-section">Inbox overview · {len(emails)} unread message(s)</div>', unsafe_allow_html=True)
    for idx, item in enumerate(emails):
        triage = classify_email(item["sender"], item["subject"], item["body"])
        p = triage["priority"]
        subject = item["subject"] or "(no subject)"
        label = f"{'🔴' if p == 'High' else '🟡' if p == 'Normal' else '⚪'}  {subject}  ·  {item['sender']}"
        with st.expander(label, expanded=(idx == 0)):
            left, right = st.columns([1.15, .85], gap="large")
            with left:
                st.markdown('<div class="mailmind-section">Message</div>', unsafe_allow_html=True)
                st.markdown(f"**From**  {item['sender']}")
                st.markdown(f"**Subject**  {subject}")
                st.text_area("Email content", value=item["body"], height=190, disabled=True, key=f"live_body_{idx}")
                draft_key = f"live_draft_{idx}"
                if st.button("✦  Generate reply draft", key=f"live_generate_{idx}", type="primary"):
                    context = f"From: {item['sender']}\nSubject: {item['subject']}\nCategory: {triage['category']}\n\nEmail body:\n{item['body']}"
                    try:
                        draft, provider, warning = generate_reply(context, return_provider=True)
                        st.session_state[draft_key] = draft
                        st.session_state[f"live_provider_{idx}"] = provider
                        st.session_state[f"live_warning_{idx}"] = warning
                    except Exception:
                        st.session_state[f"live_error_{idx}"] = "Draft generation failed. Try again later."
                if st.session_state.get(draft_key):
                    st.markdown('<div class="mailmind-section">Reply studio</div>', unsafe_allow_html=True)
                    st.text_area("Edit your reply", key=draft_key, height=170)
                    provider = st.session_state.get(f"live_provider_{idx}", "rules")
                    st.caption("Draft engine: " + ("Gemini AI" if provider == "gemini" else "Local rules fallback"))
                    warning = st.session_state.get(f"live_warning_{idx}")
                    # Provider fallback is already shown in the draft-engine caption; avoid a redundant warning banner.
                    recipient = item["sender"].strip()
                    st.caption(f"Reply recipient · {recipient}")
                    confirm_key = f"live_send_confirm_{idx}"
                    already_sent_key = f"live_sent_{idx}"
                    st.checkbox("I reviewed this reply and want to send it.", key=confirm_key)
                    if st.button("✉  Send reviewed reply", key=f"live_send_{idx}", type="primary", disabled=not st.session_state.get(confirm_key, False) or st.session_state.get(already_sent_key, False)):
                        try:
                            send_email(username, password, recipient, item.get("subject", ""), st.session_state[draft_key])
                            st.session_state[already_sent_key] = True
                            st.session_state[f"live_send_status_{idx}"] = f"Reply sent successfully to {recipient}."
                        except Exception as exc:
                            st.session_state[f"live_send_status_{idx}"] = f"Sending failed: {exc}"
                    if st.session_state.get(already_sent_key):
                        st.success(st.session_state.get(f"live_send_status_{idx}", "Reply sent successfully."))
                    elif st.session_state.get(f"live_send_status_{idx}"):
                        st.error(st.session_state[f"live_send_status_{idx}"])
                    if st.button("Clear draft", key=f"live_clear_{idx}"):
                        st.session_state.pop(draft_key, None)
                        st.session_state.pop(confirm_key, None)
                        st.rerun()
                if st.session_state.get(f"live_error_{idx}"):
                    st.error(st.session_state[f"live_error_{idx}"])
            with right:
                st.markdown('<div class="mailmind-section">Smart triage</div>', unsafe_allow_html=True)
                st.metric("Category", triage["category"])
                metrics = st.columns(2)
                metrics[0].metric("Priority", triage["priority"])
                metrics[1].metric("Automated", "Likely" if triage["automated"] else "Unlikely")
                st.markdown("**Why it was flagged**")
                st.caption(triage["reason"])
                st.markdown("**Recommended next step**")
                st.info(triage["suggested_action"])
                st.markdown('<div class="mailmind-note">Classification is rule-based and may be imperfect. Review before acting.</div>', unsafe_allow_html=True)
else:
    if "live_emails" in st.session_state:
        st.markdown('<div class="mailmind-note">No unread emails found. Send a test email to the connected mailbox or check Gmail Inbox/Spam folders.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="mailmind-note">Your inbox is ready. Click <b>Refresh unread inbox</b> to load your messages.</div>', unsafe_allow_html=True)

st.divider()
st.caption("MailMind · Experimental prototype · Inbox fetching is read-only. Replies require review and explicit send confirmation.")
