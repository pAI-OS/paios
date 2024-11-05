import aiosmtplib
import secrets
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .utils import get_env_key  # Assuming get_env_key is in utils module

async def send(to, subject, body_text, body_html = None):
    # sends mail via SMTP in text and/or html format
    # asyncio.run(send("samj@samj.net", "pAI-OS started up", f"You can access pAI-OS at https://{host}:{port}."))

    # Retrieve SMTP server details from environment variables
    smtp_host = get_env_key('PAIOS_SMTP_HOST', 'localhost')
    smtp_port = get_env_key('PAIOS_SMTP_PORT', '1025') # Default SMTP port for STARTTLS
    smtp_from = get_env_key('PAIOS_SMTP_FROM', 'paios@localhost')
    smtp_user = get_env_key('PAIOS_SMTP_USER', 'paios@localhost')
    smtp_pass = get_env_key('PAIOS_SMTP_PASS', secrets.token_urlsafe(32))

    # Create a MIME message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = smtp_from
    msg['To'] = to

    # Ensure body_html is not None
    if body_html is None:
        body_html = body_text  # Fallback to plain text if HTML is not provided

    # Attach both plain text and HTML parts
    part1 = MIMEText(body_text, 'plain')
    part2 = MIMEText(body_html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    # Connect to the SMTP server and send the email
    try:
        await aiosmtplib.send(
            msg,
            hostname=smtp_host,
            port=smtp_port,
            start_tls=False,
            username=None,
            password=None,
        )
    except Exception as e:
        print(f"Failed to send email: {e}")
