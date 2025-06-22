from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

# from apps.accounts.models import User
from django.contrib.auth.models import User

from apps.products.models import Product


class Order(TimeStampedModel):
    """Enhanced order model with delivery and payment info"""

    class Status(models.TextChoices):
        NEW = "new", _("Новый")
        PROCESSING = "processing", _("В процессе")
        SHIPPED = "shipped", _("Отправлен")
        DELIVERED = "delivered", _("Доставлен")
        COMPLETED = "completed", _("Завершен")
        CANCELLED = "cancelled", _("Отменен")

    class DeliveryMethod(models.TextChoices):
        POST = "post", _("Почта России")
        CDEK = "cdek", _("СДЭК")
        PICKUP = "pickup", _("Самовывоз")

    class PaymentMethod(models.TextChoices):
        CARD = "card", _("Кредитная карта")
        CASH = "cash", _("Наличными")

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", _("Ожидает")
        PAID = "paid", _("Оплачено")
        FAILED = "failed", _("Сбой")
        REFUNDED = "refunded", _("Возвращено")

    user = models.ForeignKey(
        User,
        verbose_name=_("user"),
        related_name="orders",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    status = models.CharField(
        _("статус"), max_length=20, choices=Status.choices, default=Status.NEW
    )
    payment_status = models.CharField(
        _("статус оплаты"),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    payment_method = models.CharField(
        _("метод оплаты"),
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD,
    )
    delivery_method = models.CharField(
        _("способ доставки"),
        max_length=20,
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.POST,
    )
    delivery_cost = models.DecimalField(
        _("стоимость доставки"), max_digits=10, decimal_places=2, default=0
    )
    total_cost = models.DecimalField(
        _("итого"), max_digits=10, decimal_places=2, default=0
    )

    # Contact information
    first_name = models.CharField(_("имя"), max_length=100)
    last_name = models.CharField(_("фамилия"), max_length=100)
    email = models.EmailField(_("адрес электронной почты"))
    phone = models.CharField(_("номер телефона"), max_length=20)

    # Delivery information
    address = models.TextField(_("адрес"), blank=True)
    postal_code = models.CharField(_("индекс"), max_length=20, blank=True)
    city = models.CharField(_("город"), max_length=100, blank=True)
    country = models.CharField(_("страна"), max_length=100, blank=True)

    # CDEK specific fields
    cdek_point_id = models.CharField(
        _("СДЭК ПВЗ ID point ID"), max_length=50, blank=True
    )
    cdek_point_address = models.TextField(_("СДЭК ПВЗ адрес"), blank=True)

    # Additional fields
    need_consultation = models.BooleanField(_("нужна консультация"), default=False)
    notes = models.TextField(_("примечание к заказу"), blank=True)

    promo_code = models.ForeignKey(
        "discounts.PromoCode",
        verbose_name=_("промо код"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    discount_amount = models.DecimalField(
        _("размер скидки"), max_digits=10, decimal_places=2, default=0
    )

    # @property
    # def total(self):
    #     return self.subtotal - self.discount_amount

    # def subtotal(self):
    #     return sum(item.cost for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.price * item.quantity for item in self.items.all())

    @property
    def total_with_discount(self):
        if self.promo_code:
            return self.subtotal - self.discount_amount + self.delivery_cost
        return self.subtotal + self.delivery_cost

    def calculate_total(self):
        # subtotal = sum(item.cost for item in self.items.all())
        return self.subtotal - self.discount_amount + self.delivery_cost

    # def save(self, *args, **kwargs):
    #     if not self.total_cost:
    #         self.total_cost = self.calculate_total()
    #     super().save(*args, **kwargs)

    # def calculate_total(self):
    #     return sum(item.cost for item in self.items.all()) + self.delivery_cost

    # @property
    # def total_quantity(self):
    #     return sum(item.quantity for item in self.items.all())

    def save(self, *args, **kwargs):
        if not hasattr(self, "discount_amount") or not self.discount_amount:
            if self.promo_code:
                self.discount_amount = self.promo_code.apply_discount(self.subtotal)
            else:
                self.discount_amount = 0
        super().save(*args, **kwargs)

    payment_id = models.CharField(
        max_length=100, blank=True, verbose_name="ID оплаты в Yookassa"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Ожидание оплаты"),
            ("waiting_for_capture", "Ожидание подтверждения оплаты"),
            ("succeeded", "Оплачен"),
            ("canceled", "Отменен"),
            ("refunded", "Возрат денег"),
        ],
        default="pending",
        verbose_name="Статус оплаты",
    )
    payment_data = models.JSONField(
        blank=True, null=True, verbose_name="Ответ Yookassa"
    )
    paid_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Временная метка оплаты"
    )

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
        ordering = ["-created"]

    def __str__(self):
        return f"Order #{self.id} - {self.get_payment_status_display()}"


class OrderItem(models.Model):
    """Items included in an order"""

    order = models.ForeignKey(
        Order, verbose_name=_("заказ"), related_name="items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("продукт"),
        related_name="order_items",
        on_delete=models.PROTECT,
    )
    price = models.DecimalField(_("цена"), max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(_("количество"), default=1)

    @property
    def cost(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = _("позиция")
        verbose_name_plural = _("позиции")

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
