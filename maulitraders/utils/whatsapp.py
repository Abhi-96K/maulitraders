import os
from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_whatsapp_message(to_number, message_body):
    """
    Sends a WhatsApp message using Twilio.
    to_number: The recipient's number (e.g., '+919876543210')
    message_body: The text content of the message
    """
    try:
        # Check if settings are configured
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN or not settings.TWILIO_WHATSAPP_NUMBER:
            logger.warning("Twilio settings are not fully configured. Notification skipped.")
            return False

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Ensure number has 'whatsapp:' prefix
        from_number = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"
        if not to_number.startswith('whatsapp:'):
            # Assumes number is already in E.164 format (e.g. +91...) or local. 
            # Twilio for WhatsApp usually requires 'whatsapp:+' prefix.
            # If input is just '9876543210', we might need to add country code, but let's assume valid 'to_number' passed.
            to_number_formatted = f"whatsapp:{to_number}"
        else:
            to_number_formatted = to_number

        message = client.messages.create(
            from_=from_number,
            body=message_body,
            to=to_number_formatted
        )
        logger.info(f"WhatsApp message sent to {to_number}: SID={message.sid}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message to {to_number}: {str(e)}")
        return False
