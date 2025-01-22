import requests
from django.conf import settings
import hmac
import hashlib
import logging



logger = logging.getLogger(__name__)

class PaystackMixin:
    PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
    PAYSTACK_BASE_URL = "https://api.paystack.co"

    def initialize_payment(self, email, amount, callback_url=None):
        """
        Initializes a payment with Paystack
        """
        try:
            url = f"{self.PAYSTACK_BASE_URL}/transaction/initialize"

            headers = {
                "Authorization": f"Bearer {self.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            amount_in_kobo = int(amount * 100)

            payload = {
                "email": email,
                "amount": amount_in_kobo,
                "callback_url": callback_url
            }
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack Initialization Error: {str(e)}")
            raise ValueError("Error initializing payment")
    
    def verify_payment(self, reference):
        """
        Verifies a payment with Paystack
        """
        try:
            url = f"{self.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
            headers = {
                "Authorization": f"Bearer {self.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack Verification Error: {str(e)}")
            raise ValueError("Error verifying payment")
        
    def verify_webhook_signature(self, payload, signature):
        """
        Verifies that the webhook is from Paystack
        """
        computed_hmac = hmac.new(
            self.PAYSTACK_SECRET_KEY.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        return hmac.compare_digest(computed_hmac, signature)
        
    