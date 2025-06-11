from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from apps.users.models import User
from apps.products.models import Product


class Order(TimeStampedModel):
    """Order model for customer purchases"""

    class Status(models.TextChoices):
        NEW = "new", _("New")
        PROCESSING = "processing", _("Processing")
        SHIPPED = "shipped", _("Shipped")
        DELIVERED = "delivered", _("Delivered")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    user = models.ForeignKey(
        User,
        verbose_name=_("user"),
        related_name="orders",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    status = models.CharField(
        _("status"), max_length=20, choices=Status.choices, default=Status.NEW
    )
    first_name = models.CharField(_("first name"), max_length=100)
    last_name = models.CharField(_("last name"), max_length=100)
    email = models.EmailField(_("email"))
    phone = models.CharField(_("phone"), max_length=20)
    address = models.TextField(_("address"), blank=True)
    postal_code = models.CharField(_("postal code"), max_length=20, blank=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    country = models.CharField(_("country"), max_length=100, blank=True)
    need_consultation = models.BooleanField(_("need consultation"), default=False)
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")
        ordering = ["-created"]

    def __str__(self):
        return f"Order #{self.pk}"

    @property
    def total_cost(self):
        return sum(item.cost for item in self.items.all())


class OrderItem(models.Model):
    """Items included in an order"""

    order = models.ForeignKey(
        Order, verbose_name=_("order"), related_name="items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("product"),
        related_name="order_items",
        on_delete=models.PROTECT,
    )
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(_("quantity"), default=1)

    class Meta:
        verbose_name = _("order item")
        verbose_name_plural = _("order items")

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def cost(self):
        return self.price * self.quantity
