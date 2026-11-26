"""Lightweight local email triage. No external API calls, no actions taken."""
import re

RULES = [
    ("job", ("recruiter", "job opportunity", "job opening", "application", "interview", "hiring", "resume", "cv")),
    ("meeting", ("meeting", "calendar invite", "schedule", "availability", "zoom", "teams call")),
    ("billing", ("invoice", "payment", "bill", "refund", "receipt", "quotation", "quote", "pricing")),
    ("complaint", ("complaint", "issue", "problem", "not working", "broken", "wrong", "disappointed")),
    ("delivery", ("delivery", "shipment", "tracking", "order", "dispatched", "courier")),
    ("promotion", ("sale", "discount", "offer", "promo", "newsletter", "unsubscribe")),
    ("security", ("password", "verify your account", "verification", "suspicious login", "otp", "security alert")),
    ("personal", ("hey", "hi", "hello", "how are you", "miss you", "love", "friend")),
]

URGENT_TERMS = ("urgent", "asap", "immediately", "today", "deadline", "action required", "final notice", "overdue")
AUTOMATED_TERMS = ("no-reply", "noreply", "do-not-reply", "mailer-daemon", "newsletter")


def classify_email(sender, subject, body):
    """Return a category, priority, reason, and safe suggested next step."""
    text = f"{subject or ''} {body or ''}".lower()
    sender_lower = (sender or "").lower()
    category = "general"
    for label, terms in RULES:
        if any(term in text for term in terms):
            category = label
            break
    urgent = any(term in text for term in URGENT_TERMS)
    automated = any(term in sender_lower for term in AUTOMATED_TERMS) or category == "promotion"
    priority = "high" if urgent or category in ("security", "complaint", "job") else "low" if automated else "normal"
    reason = "Urgency keywords detected." if urgent else f"Matched {category} email patterns." if category != "general" else "No specific pattern matched."
    actions = {
        "job": "Review the opportunity and decide whether to respond.",
        "meeting": "Check the proposed time and confirm or ask for details.",
        "billing": "Verify amounts and account details before taking action.",
        "complaint": "Review the issue and prepare a careful response.",
        "delivery": "Check tracking or order status before promising an update.",
        "promotion": "No reply is usually needed. Consider reviewing or ignoring.",
        "security": "Verify through the official site or app. Never share passwords or OTPs.",
        "personal": "Reply naturally if a response is appropriate.",
        "general": "Read the message and decide whether it needs a reply.",
    }
    return {
        "category": category.title(),
        "priority": priority.title(),
        "automated": automated,
        "reason": reason,
        "suggested_action": actions[category],
    }
