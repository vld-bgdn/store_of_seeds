from django.conf import settings
from django.urls import reverse


class YandexPay:
    """Yandex Pay integration (mock version)"""

    def __init__(self, order):
        self.order = order
        self.merchant_id = settings.YANDEX_PAY_MERCHANT_ID
        self.secret_key = settings.YANDEX_PAY_SECRET_KEY

    def create_payment(self):
        """Create payment request (mock version)"""
        return {
            "success": True,
            "payment_id": f"yp_{self.order.id}",
            "amount": str(self.order.total_cost),
            "currency": "RUB",
            "confirmation_url": reverse("orders:payment_process"),
        }

    def verify_payment(self, payment_data):
        """Verify payment (mock version)"""
        return True

    def get_js_widget(self):
        """Get JS widget code for Yandex Pay (mock version)"""
        return """
        <div style="border: 2px dashed #ccc; padding: 20px; text-align: center;">
            <p>Yandex Pay Widget (demo mode)</p>
            <p>Order #{} - {} RUB</p>
        </div>
        """.format(
            self.order.id, self.order.total_cost
        )
