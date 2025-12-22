from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_html_email(subject, template_name, context, recipient_list):
    """
    Sends an HTML email with a plain text fallback.
    """
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    
    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            recipient_list,
            html_message=html_message
        )
        print(f"DEBUG: HTML Email '{subject}' sent to {recipient_list}")
        return True
    except Exception as e:
        print(f"DEBUG: Failed to send HTML email: {e}")
        return False

def send_whatsapp_message(mobile, message):
    """
    Placeholder for sending WhatsApp messages.
    Integrate with Twilio, Meta API, or other providers here.
    """
    print("="*50)
    print(f"WHATSAPP MESSAGE to {mobile}:")
    print(message)
    print("="*50)
    # Example using Twilio (You need to install twilio: pip install twilio)
    from twilio.rest import Client
    
    try:
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            print("DEBUG: Twilio credentials missing in settings.")
            return False

        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        
        from_whatsapp_number = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}" if settings.TWILIO_WHATSAPP_NUMBER else 'whatsapp:+14155238886'
        to_whatsapp_number = f'whatsapp:+91{mobile}' # Ensure country code
    
        client = Client(account_sid, auth_token)
    
        message = client.messages.create(
            body=message,
            from_=from_whatsapp_number,
            to=to_whatsapp_number
        )
        print(f"DEBUG: WhatsApp sent! SID: {message.sid}")
        return True
    except Exception as e:
        print(f"DEBUG: Failed to send WhatsApp: {e}")
        return False
    
    # Placeholder log for now
    print("="*50)
    print(f"WHATSAPP MESSAGE to {mobile}:")
    print(message)
    print("="*50)
    return True
