from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

# from apps.accounts.models import User
from django.contrib.auth.models import User

from apps.products.models import Product


class Order(TimeStampedModel):
    """Enhanced order model with delivery and payment info"""

    class Status(models.TextChoices):
        NEW = "new", _("New")
        PROCESSING = "processing", _("Processing")
        SHIPPED = "shipped", _("Shipped")
        DELIVERED = "delivered", _("Delivered")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    class DeliveryMethod(models.TextChoices):
        POST = "post", _("Russian Post")
        CDEK = "cdek", _("CDEK")
        PICKUP = "pickup", _("Pickup")

    class PaymentMethod(models.TextChoices):
        YANDEX = "yandex", _("Yandex Pay")
        CARD = "card", _("Credit Card")
        CASH = "cash", _("Cash on Delivery")

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        PAID = "paid", _("Paid")
        FAILED = "failed", _("Failed")
        REFUNDED = "refunded", _("Refunded")

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
    payment_status = models.CharField(
        _("payment status"),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    payment_method = models.CharField(
        _("payment method"),
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.YANDEX,
    )
    delivery_method = models.CharField(
        _("delivery method"),
        max_length=20,
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.POST,
    )
    delivery_cost = models.DecimalField(
        _("delivery cost"), max_digits=10, decimal_places=2, default=0
    )
    total_cost = models.DecimalField(
        _("total cost"), max_digits=10, decimal_places=2, default=0
    )

    # Contact information
    first_name = models.CharField(_("first name"), max_length=100)
    last_name = models.CharField(_("last name"), max_length=100)
    email = models.EmailField(_("email"))
    phone = models.CharField(_("phone"), max_length=20)

    # Delivery information
    address = models.TextField(_("address"), blank=True)
    postal_code = models.CharField(_("postal code"), max_length=20, blank=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    country = models.CharField(_("country"), max_length=100, blank=True)

    # CDEK specific fields
    cdek_point_id = models.CharField(_("CDEK point ID"), max_length=50, blank=True)
    cdek_point_address = models.TextField(_("CDEK point address"), blank=True)

    # Additional fields
    need_consultation = models.BooleanField(_("need consultation"), default=False)
    notes = models.TextField(_("notes"), blank=True)
    ip_address = models.GenericIPAddressField(_("IP address"), blank=True, null=True)

    promo_code = models.ForeignKey(
        "discounts.PromoCode",
        verbose_name=_("promo code"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    discount_amount = models.DecimalField(
        _("discount amount"), max_digits=10, decimal_places=2, default=0
    )

    def calculate_total(self):
        subtotal = sum(item.cost for item in self.items.all())
        return subtotal - self.discount_amount + self.delivery_cost

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
        ordering = ["-created"]

    def __str__(self):
        return f"Order #{self.pk}"

    # def save(self, *args, **kwargs):
    #     if not self.total_cost:
    #         self.total_cost = self.calculate_total()
    #     super().save(*args, **kwargs)

    # def calculate_total(self):
    #     return sum(item.cost for item in self.items.all()) + self.delivery_cost

    @property
    def subtotal(self):
        return sum(item.price * item.quantity for item in self.items.all())

    @property
    def total_with_discount(self):
        if self.promo_code:
            return self.subtotal - self.discount_amount + self.delivery_cost
        return self.subtotal + self.delivery_cost

    def save(self, *args, **kwargs):
        if not hasattr(self, "discount_amount") or not self.discount_amount:
            if self.promo_code:
                self.discount_amount = self.promo_code.apply_discount(self.subtotal)
            else:
                self.discount_amount = 0
        super().save(*args, **kwargs)


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

    @property
    def cost(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = _("order item")
        verbose_name_plural = _("order items")

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
