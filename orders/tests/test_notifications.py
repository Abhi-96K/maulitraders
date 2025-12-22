from django.test import TestCase
from unittest.mock import patch, MagicMock
from maulitraders.utils.whatsapp import send_whatsapp_message
from orders.signals import send_status_update_notification
from orders.models import Order
from orders.models import Order
from django.conf import settings

class NotificationTest(TestCase):
    @patch('maulitraders.utils.whatsapp.Client')
    def test_send_whatsapp_message(self, MockClient):
        # Setup mock
        mock_messages = MockClient.return_value.messages
        mock_messages.create.return_value.sid = 'SM123'
        
        # Test Function
        # We need to temporarily set settings if not set, but assuming test runner has them or we mock them
        with patch.object(settings, 'TWILIO_ACCOUNT_SID', 'AC123'), \
             patch.object(settings, 'TWILIO_AUTH_TOKEN', 'token'), \
             patch.object(settings, 'TWILIO_WHATSAPP_NUMBER', '+14155238886'):
             
             result = send_whatsapp_message('+919876543210', 'Test Message')
             
             self.assertTrue(result)
             mock_messages.create.assert_called_once()
             args, kwargs = mock_messages.create.call_args
             self.assertEqual(kwargs['to'], 'whatsapp:+919876543210')
             self.assertEqual(kwargs['body'], 'Test Message')

class SignalTest(TestCase):
    @patch('orders.signals.send_whatsapp_message')
    def test_status_change_signal(self, mock_send):
        # Create Order
        order = Order.objects.create(customer_name="Test", customer_mobile="9876543210")
        
        # Initial create should NOT call signal (handled in view)
        # However, our signal handler for created=True returns early, so this assumes default.
        mock_send.assert_not_called()
        
        # Change status
        order.status = 'SHIPPED'
        order.save()
        
        # Check if called
        mock_send.assert_called_once()
        args, _ = mock_send.call_args
        self.assertEqual(args[0], '+919876543210')
        self.assertIn('shipped', args[1].lower())
