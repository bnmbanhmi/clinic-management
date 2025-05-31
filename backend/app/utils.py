import smtplib
from email.mime.text import MIMEText
from app.config import settings

def send_email(to_email: str, subject: str, body: str):
    # For local debugging, username and password might not be needed
    # Only enforce username/password if not using localhost or if they are explicitly set for localhost
    is_localhost_debug = settings.MAIL_SERVER == "localhost" and settings.MAIL_PORT == 1025
    
    required_settings = [settings.MAIL_SERVER, settings.MAIL_FROM]
    if not is_localhost_debug: # For non-localhost or if localhost requires auth
        required_settings.extend([settings.MAIL_USERNAME, settings.MAIL_PASSWORD])

    if not all(required_settings):
        print("Email settings (MAIL_SERVER, MAIL_FROM, and potentially MAIL_USERNAME, MAIL_PASSWORD for non-local servers) are not fully configured.")
        # Depending on desired behavior, you might raise an exception here
        # For now, just printing an error and returning to avoid crashing if email is optional
        return

    msg = MIMEText(body, 'html') # Specify HTML content type for the body
    msg['Subject'] = subject
    # Ensure MAIL_FROM is not None before assignment
    mail_from = str(settings.MAIL_FROM) # Cast to string, though check above should ensure it's not None
    msg['From'] = mail_from
    msg['To'] = to_email

    try:
        # Ensure MAIL_SERVER and MAIL_USERNAME/PASSWORD are not None
        mail_server_host = str(settings.MAIL_SERVER)
        
        with smtplib.SMTP(mail_server_host, settings.MAIL_PORT) as server:
            if settings.MAIL_USE_TLS:
                server.starttls()
            # Only login if username and password are provided (and not localhost debug without them)
            if settings.MAIL_USERNAME and settings.MAIL_PASSWORD:
                 mail_username = str(settings.MAIL_USERNAME)
                 mail_password = str(settings.MAIL_PASSWORD)
                 server.login(mail_username, mail_password)
            elif not is_localhost_debug and (not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD):
                print("MAIL_USERNAME or MAIL_PASSWORD missing for non-localhost SMTP server.")
                return # Or raise error

            server.sendmail(mail_from, [to_email], msg.as_string())
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_password_reset_email(email: str, token: str):
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    subject = "Password Reset Request"
    # Corrected f-string syntax and ensure body is HTML
    body = f"""<!DOCTYPE html>
    <html>
    <body>
        <p>Hello,</p>
        <p>You requested a password reset. Click the link below to reset your password:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>If you did not request this, please ignore this email.</p>
        <p>This link will expire in 1 hour.</p>
        <p>Thanks,</p>
        <p>The Clinic Management Team</p>
    </body>
    </html>"""
    send_email(to_email=email, subject=subject, body=body)
