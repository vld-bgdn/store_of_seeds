import requests
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class TelegramBot:
    """Simple Telegram bot for order notifications"""

    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

    def send_message(self, text):
        """Send message to Telegram chat"""
        if not self.token or not self.chat_id:
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}

        try:
            response = requests.post(url, data=payload)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def notify_new_order(self, order):
        """Send notification about new order"""
        text = (
            f"<b>Новый заказ #{order.id}</b>\n"
            f"Имя: {order.first_name} {order.last_name}\n"
            f"Телефон: {order.phone}\n"
            f"Email: {order.email}\n"
            f"Сумма: {order.calculate_total} ₽\n"
            f"Способ доставки: {order.get_delivery_method_display()}\n"
            f"Способ оплаты: {order.get_payment_method_display()}\n"
        )

        if order.need_consultation:
            text += "\n⚠️ <b>Требуется консультация</b>"

        return self.send_message(text)

    def notify_payment(self, order):
        """Send notification about payment"""
        text = (
            f"<b>Оплачен заказ #{order.id}</b>\n"
            f"Статус: {order.get_payment_status_display()}\n"
            f"Сумма: {order.calculate_total} ₽\n"
        )
        return self.send_message(text)
