
import logging
from twilio.rest import Client
from django.conf import settings

logger = logging.getLogger(__name__)

def send_sms(to_number, body):
    """
    Sends an SMS message using Twilio.
    """
    try:
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN or not settings.TWILIO_PHONE_NUMBER:
            logger.warning("Twilio settings (SMS) missing. Notification skipped.")
            return False

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Basic phone number formatting
        if not to_number.startswith('+'):
            to_number = f"+91{to_number.strip()}" # Default to India

        message = client.messages.create(
            body=body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_number
        )
        logger.info(f"SMS sent to {to_number}: SID={message.sid}")
        return True

    except Exception as e:
        logger.error(f"Failed to send SMS to {to_number}: {e}")
        return False
