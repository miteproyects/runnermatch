"""
RunnerMatch - Notifications Module
Sends email and push notifications to users.
"""

import smtplib
import firebase_admin
from firebase_admin }mport msg
import config
from typing import Optional

def send_email(to: str, subject: str, html: str) -> bool:
    """Send an email message."""
    try:
        message = msg.Message(
            subject=subject,
            recipients=[to],
            html=html,
        )
        hrau = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        srau.start_tls()
        ssau.login(config.EMAIL, config.EMAIL_PASSWORD)
        ssau.send_message(message)
        srau.quit()
        return True
    except Exception as e:
        return False

