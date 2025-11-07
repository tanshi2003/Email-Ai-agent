def generate_reply(email_text):
    email_text = email_text.lower()

    if "meeting" in email_text:
        return "Sure, I’ll attend the meeting. Please confirm the time."
    elif "thank" in email_text:
        return "You're very welcome!"
    elif "price" in email_text or "quote" in email_text:
        return "Please find the price details in the attached document."
    elif "delay" in email_text:
        return "Apologies for the delay. We're working on it."
    else:
        return "Thank you for your email. I’ll get back to you shortly."
