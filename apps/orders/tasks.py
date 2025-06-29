from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils.html import strip_tags

# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings
from .models import Order
from .telegram import TelegramBot


@shared_task
def order_status_changed(order_id):
    """
    Task to send notifications when order status changes
    """
    order = Order.objects.get(id=order_id)

    subject = f"Стутс заказа #{order.id} изменен на {order.get_status_display()}"

    context = {
        "order": order,
        "status": order.get_status_display(),
    }

    html_message = render_to_string("orders/email/order_status_changed.html", context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        html_message=html_message,
        fail_silently=False,
    )
    # Additional notifications could be added here (SMS, push, etc.)


@shared_task
def order_created(order_id):
    """Task to send email notification when an order is created"""
    order = Order.objects.get(id=order_id)
    subject = f"Заказ #{order.id} сформирован"
    html_message = render_to_string("orders/email/order_created.html", {"order": order})
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        html_message=html_message,
        fail_silently=False,
    )

    # Send Telegram notification
    bot = TelegramBot()
    bot.notify_new_order(order)


@shared_task
def payment_received(order_id):
    """Task to send email notification when payment is received"""
    order = Order.objects.get(id=order_id)
    subject = f"Получена оплата по заказу #{order.id}"
    html_message = render_to_string(
        "orders/email/payment_received.html", {"order": order}
    )
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        html_message=html_message,
        fail_silently=False,
    )

    # Send Telegram notification
    bot = TelegramBot()
    bot.notify_payment(order)
