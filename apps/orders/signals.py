from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from .models import Order
from .tasks import order_status_changed
from .telegram import TelegramBot


@receiver(post_save, sender=Order)
def order_status_change_handler(sender, instance, created, **kwargs):
    """Handle order status changes"""
    if not created:
        # Notify about status changes
        order_status_changed.delay(instance.id)

        # Notify Telegram about important changes
        bot = TelegramBot()
        if instance.status == Order.Status.SHIPPED:
            bot.send_message(
                f"<b>Заказ #{instance.id} отправлен</b>\n"
                f"Способ доставки: {instance.get_delivery_method_display()}\n"
                f"Трек-номер: {instance.tracking_number or 'не указан'}"
            )
        elif instance.status == Order.Status.COMPLETED:
            bot.send_message(
                f"<b>Заказ #{instance.id} завершен</b>\n"
                f"Клиент: {instance.first_name} {instance.last_name}"
            )
