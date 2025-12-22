import os
import django
from django.core.mail import send_mail
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maulitraders.settings')
django.setup()

def test_send_email():
    subject = 'Test Email from Mauli Traders'
    message = 'This is a test email to verify the email configuration.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['1.maulitraders@gmail.com'] # Sending to self to test

    print(f"Attempting to send email...")
    print(f"From: {from_email}")
    print(f"To: {recipient_list}")
    print(f"Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    print(f"User: {settings.EMAIL_HOST_USER}")

    try:
        send_mail(subject, message, from_email, recipient_list)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == '__main__':
    test_send_email()
