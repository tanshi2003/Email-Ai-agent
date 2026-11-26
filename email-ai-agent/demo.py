"""Local sample-data demo. Never connects to or sends from a real inbox."""
import streamlit as st
from dotenv import load_dotenv

from ai_logic import generate_reply

load_dotenv()
st.set_page_config(page_title="MailMind | Email Agent Demo", page_icon="✉️", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1100px; padding-top: 2.5rem;}
.hero {padding: 2.2rem; border-radius: 22px; background: linear-gradient(130deg,#171a32,#32345f); color: white; margin-bottom: 1.5rem;}
.hero p {color:#d3d5ef; font-size:1.02rem;}
.pill {display:inline-block; border:1px solid #8b8ec4; border-radius:99px; padding:4px 10px; font-size:.75rem; color:#dedfff;}
.provider-pill {display:inline-block; border-radius:99px; padding:5px 12px; font-size:.78rem; font-weight:600; margin-bottom:.5rem;}
</style>
<div class="hero">
  <span class="pill">LOCAL INTERACTIVE DEMO · SAMPLE DATA ONLY</span>
  <h1 style="font-size:2.7rem;margin:.7rem 0 .25rem;">MailMind</h1>
  <p style="margin:0;">An email assistant that turns incoming messages into thoughtful reply drafts.</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1, 1], gap="large")
with left:
    st.subheader("01 / Incoming email")
    sample = st.selectbox("Try a sample", ["Project meeting", "Pricing enquiry", "Delivery delay", "Thank-you note", "Write my own"])
    samples = {
        "Project meeting": ("Meeting schedule", "Hi, can you confirm if you will attend tomorrow's project meeting?"),
        "Pricing enquiry": ("Request for quotation", "Hello, could you please share the price and quote for your services?"),
        "Delivery delay": ("Order update", "Our delivery has been delayed. Can you let us know the status?"),
        "Thank-you note": ("Thank you", "Thank you for your help and support on this project."),
    }
    if sample == "Write my own":
        subject = st.text_input("Subject", "A quick question")
        body = st.text_area("Email body", height=210, placeholder="Write a fictional sample email here...")
    else:
        subject, body = samples[sample]
        st.text_input("Subject", value=subject, disabled=True)
        st.text_area("Email body", value=body, height=210, disabled=True)
    st.caption("Use fictional sample content only. Avoid pasting private or confidential emails.")

email_input = f"Subject: {subject}\\n\\n{body}"
with right:
    st.subheader("02 / Generated reply")
    st.write("Generate a draft based on the selected email.")
    if st.button("Generate reply draft", type="primary", use_container_width=True):
        for key in ("draft", "draft_provider", "draft_warning", "draft_error"):
            st.session_state.pop(key, None)
        st.session_state["current_email"] = email_input
        try:
            draft, used_provider, warning = generate_reply(email_input, return_provider=True)
            st.session_state["draft"] = draft
            st.session_state["draft_output"] = draft
            st.session_state["draft_provider"] = used_provider
            if warning:
                st.session_state["draft_warning"] = warning
        except Exception:
            st.session_state["draft_error"] = "AI drafting is temporarily unavailable. Please try again in a moment."

    if st.session_state.get("draft"):
        provider = st.session_state.get("draft_provider", "unknown")
        if provider == "gemini":
            st.success("Draft generated · Not sent")
            st.markdown('<span class="provider-pill" style="background:#123e32;color:#8ee4c1;">✦ AI MODE · Gemini</span>', unsafe_allow_html=True)
            st.caption("Drafted with Gemini. Review it carefully before using.")
        elif provider == "rules-fallback":
            st.success("Draft generated · Not sent")
            st.markdown('<span class="provider-pill" style="background:#4b3b13;color:#f3d46b;">↻ FALLBACK MODE · Backup draft</span>', unsafe_allow_html=True)
            st.warning("AI service is temporarily unavailable. A backup draft was created so you can keep going.")
            if st.button("Retry Gemini", use_container_width=True, key="retry_gemini"):
                try:
                    retry_draft = generate_reply(st.session_state.get("current_email", email_input), provider="gemini")
                    st.session_state["draft"] = retry_draft
                    st.session_state["draft_output"] = retry_draft
                    st.session_state["draft_provider"] = "gemini"
                    st.session_state.pop("draft_warning", None)
                    st.session_state.pop("draft_error", None)
                    st.rerun()
                except Exception:
                    st.session_state["draft_error"] = "Gemini is still unavailable. Your backup draft is safe. Try again shortly."
            if st.session_state.get("draft_error"):
                st.error(st.session_state["draft_error"])
        else:
            st.success("Draft generated · Not sent")
            st.markdown('<span class="provider-pill" style="background:#303044;color:#d9d9ff;">BUILT-IN MODE · Rules</span>', unsafe_allow_html=True)
            st.caption("Generated locally using the built-in reply patterns.")
        st.text_area("Reply draft", height=210, key="draft_output")
        st.download_button("Download draft", data=st.session_state["draft"], file_name="email-reply-draft.txt", mime="text/plain", use_container_width=True)
    elif st.session_state.get("draft_error"):
        st.error(st.session_state["draft_error"])
    else:
        st.info("Your generated reply will appear here. Nothing is sent from this demo.")

st.divider()
st.subheader("How the system works")
steps = st.columns(4)
for col, number, title, detail in zip(steps, ["01","02","03","04"], ["Read","Understand","Draft","Review"], ["IMAP retrieves unread email", "Reply engine processes context", "A response is prepared", "Human reviews before sending"]):
    with col:
        st.markdown(f"**{number} · {title}**")
        st.caption(detail)
st.caption("Built by Tanshi Khandelwal · Python · IMAP/SMTP · Streamlit")
