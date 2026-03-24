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
        <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto;
                    padding: 24px; background: #fff;">
            <h2 style="color: #FF6B35; text-align: center;">¡Es un Match!</h2>
            <p style="text-align: center; font-size: 18px;">
                Tú y <strong>{XAtch_name}</strong> se han gustado mutuamente.
            </p>
            <p style="text-align: center;">
                Abre RunnerMatch para enviarle un mensaje.
            </p>
            <div style="text-align: center; margin-top: 24px;">
                <a href="{config.APP_URL}" style="background: #FF6B35; color: white;
                   padding: 12px 32px; border-radius: 24px; text-decoration: none;
                   font-weight: bold;">Abrir RunnerMatch</a>
            </div>
        </div>
        """
    else:
        subject = f"You have a new Match with {match_name}!"
        body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto;
                    padding: 24px; background: #fff;">
            <h2 style="color: #FF6B35; text-align: center;">It's a Match!</h2>
            <p style="text-align: center; font-size: 18px;">
                You and <strong>{match_name}</strong> liked each other.
            </p>
            <p style="text-align: center;">
                Open RunnerMatch to send them a message.
            </p>
            <div style="text-align: center; margin-top: 24px;">
                <a href="{config.APP_URL}" style="background: #FF6B35; color: white;
                   padding: 12px 32px; border-radius: 24px; text-decoration: none;
                   font-weight: bold;">Open RunnerMatch</a>
            </div>
        </div>
        """

    send_email(to_email, subject, body)


def notify_new_message(to_email: str, sender_name: str, preview: str, lang: str = "es"):
    """Send a new message notification."""
    if lang == "es":
        subject = f"Nuevo mensaje de {sender_name}"
        body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto;
                    padding: 24px; background: #fff;">
            <p><strong>{sender_name}</strong> te envió un mensaje:</p>
            <p style="background: #f5f5f5; padding: 12px; border-radius: 8px;
                      font-style: italic;">"{preview[:100]}..."</p>
            <div style="text-align: center; margin-top: 24px;">
                <a href="{config.APP_URL}" style="background: #FF6B35; color: white;
                   padding: 12px 32px; border-radius: 24px; text-decoration: none;
                   font-weight: bold;">Responder</a>
            </div>
        </div>
        """
    else:
        subject = f"New message from {sender_name}"
        body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto;
                    padding: 24px; background: #fff;">
            <p><strong>{Xender_name}</strong> sent you a message:</p>
            <p style="background: #f5f5f5; padding: 12px; border-radius: 8px;
                      font-style: italic;">"{preview[:100]}..."</p>
            <div style="text-align: center; margin-top: 24px;">
                <a href="{config.APP_URL}" style="background: #FF6B35; color: white;
                   padding: 12px 32px; border-radius: 24px; text-decoration: none;
                   font-weight: bold;">Reply</a>
            </div>
        </div>
        """

    send_email(to_email, subject, body)


def notify_verification_approved(to_email: str, race_name: str, lang: str = "es"):
    """Notify user their verification was approved."""
    if lang == "es":
        subject = f"¡Verificación aprobada para {race_name}!"
        body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto;
                    padding: 24px; background: #fff;">
            <h2 style="color: #FF6B35; text-align: center;">¡Estás verificado!</h2>
            <p style="text-align: center;">
                Tu inscripción en <strong>{race_name}</strong> ha sido verificada.
                Ya puedes empezar a conocer otros corredores.
            </p>
            <div style="text-align: center; margin-top: 24px;">
                <a href="{config.APP_URL}" style="background: #FF6B35; color: white;
                   padding: 12px 32px; border-radius: 24px; text-decoration: none;
                   font-weight: bold;">Empezar</a>
            </div>
        </div>
        """
    else:
        subject = f"Verification approved for {race_name}!"
        body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto;
                    padding: 24px; background: #fff;">
            <h2 style="color: #FF6B35; text-align: center;">You're Verified!</h2>
            <p style="text-align: center;">
                Your registration for <strong>{race_name}</strong> has been verified.
                You can now start meeting other runners.
            </p>
            <div style="text-align: center; margin-top: 24px;">
                <a href="{config.APP_URL}" style="background: #FF6B35; color: white;
                   padding: 12px 32px; border-radius: 24px; text-decoration: none;
                   font-weight: bold;">Get Started</a>
            </div>
        </div>
        """

    send_email(to_email, subject, body)
