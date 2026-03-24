"""
RunnerMatch - Email Notifications
Sends match and message notifications via Gmail.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send an email via Gmail SMTP."""
    if not config.GMAIL_ADDRESS or not config.GMAIL_APP_PASSWORD:
        print("Gmail not configured, skipping notification.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"RunnerMatch <{config.GMAIL_ADDRESS}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD)
            server.sendmail(config.GMAIL_ADDRESS, to_email, msg.as_string())

        return True
    except Exception as e:
        print(f"Email send error: {e}")
        return False


def notify_match(to_email: str, match_name: str, lang: str = "es"):
    """Send a 'You got a match!' notification."""
    if lang == "es":
        subject = f"¡Tienes un nuevo Match con {match_name}!"
        body = f"""