from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from .models import Order
from .telegram import TelegramBot


@shared_task
def order_status_changed(order_id):
    """
    Task to send notifications when order status changes
    """
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.conf import settings
    from .models import Order

    order = Order.objects.get(id=order_id)

    # Email subject based on status
    subject = f"Order #{order.id} status changed to {order.get_status_display()}"

    # Render email template
    context = {
        "order": order,
        "status": order.get_status_display(),
        "previous_status": (
            order.history.latest().prev_record.status
            if order.history.exists()
            else None
        ),
    }

    message = render_to_string("orders/email/order_status_changed.txt", context)
    html_message = render_to_string("orders/email/order_status_changed.html", context)

    # Send email
    send_mail(
        subject,
        message,
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
    subject = _("Order #{}").format(order.id)
    message = _("Thank you for your order!")
    html_message = render_to_string("orders/email/order_created.html", {"order": order})

    send_mail(
        subject,
        message,
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
    subject = _("Payment received for order #{}").format(order.id)
    message = _("We have received your payment.")
    html_message = render_to_string(
        "orders/email/payment_received.html", {"order": order}
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        html_message=html_message,
        fail_silently=False,
    )

    # Send Telegram notification
    bot = TelegramBot()
    bot.notify_payment(order)
