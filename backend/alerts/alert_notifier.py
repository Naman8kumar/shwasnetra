import smtplib
from email.mime.text import MIMEText
import logging
from datetime import datetime
import os

# Setup logging for alert tracking
ALERT_LOG_FILE = 'backend/logs/alerts.log'
os.makedirs(os.path.dirname(ALERT_LOG_FILE), exist_ok=True)

alert_logger = logging.getLogger("alert_logger")
alert_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(ALERT_LOG_FILE)
alert_logger.addHandler(file_handler)

def send_email_alert(to_email, filename, confidence):
    subject = "🚨 Lung Cancer Alert from ShwasNetra"
    body = f"""
    Alert! A scan has been classified as CANCER by the AI.

    📄 Filename: {filename}
    📊 Confidence: {confidence}%
    🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    Please review the case immediately.
    """

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "shwasnetra@yourdomain.com"
    msg['To'] = to_email

    try:
        with smtplib.SMTP('smtp.yourdomain.com', 587) as server:
            server.starttls()
            server.login("your_email", "your_password")
            server.send_message(msg)
            alert_logger.info(f"Sent cancer alert for {filename} to {to_email}")
    except Exception as e:
        alert_logger.error(f"Failed to send alert: {str(e)}")
