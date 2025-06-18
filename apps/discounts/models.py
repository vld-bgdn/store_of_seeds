from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from django.core.validators import MinValueValidator, MaxValueValidator

# from apps.accounts.models import User
from django.contrib.auth.models import User

from django.utils import timezone


class PromoCode(TimeStampedModel):
    """Promo code for discounts"""

    class DiscountType(models.TextChoices):
        PERCENT = "percent", _("Процент")
        FIXED = "fixed", _("Фиксированная сумма")

    code = models.CharField(_("Код"), max_length=20, unique=True)
    discount_type = models.CharField(
        _("тип скидки"),
        max_length=10,
        choices=DiscountType.choices,
        default=DiscountType.PERCENT,
    )
    discount_value = models.DecimalField(
        _("размер скидки"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    max_discount = models.DecimalField(
        _("размер максимальной скидки"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        help_text=_("Максимальная скидка для процентных скидок"),
    )
    min_order_amount = models.DecimalField(
        _("минимальная сумма заказа"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        help_text=_("Минимальная сумма заказа для применения скидки"),
    )
    valid_from = models.DateTimeField(_("Действует с"))
    valid_to = models.DateTimeField(_("Действует до"))
    active = models.BooleanField(_("active"), default=True)
    max_uses = models.PositiveIntegerField(
        _("максимальное использование uses"),
        blank=True,
        help_text=_("Максимально количество раз, когда можно использовать этот код"),
        default=200,
    )
    current_uses = models.PositiveIntegerField(_("current uses"), default=0)
    for_all_users = models.BooleanField(_("for all users"), default=True)
    for_first_order = models.BooleanField(_("for first order only"), default=False)

    class Meta:
        verbose_name = _("Промо код")
        verbose_name_plural = _("Промо коды")
        ordering = ["-created"]

    def __str__(self):
        return self.code

    def is_valid(self, user=None, order_total=None):
        """Check if promo code is valid for the given user and order total"""
        now = timezone.now()

        if not self.active:
            return False

        if now < self.valid_from or now > self.valid_to:
            return False

        if self.max_uses and self.current_uses >= self.max_uses:
            return False

        if (
            order_total
            and self.min_order_amount
            and order_total < self.min_order_amount
        ):
            return False

        if (
            not self.for_all_users
            and user
            and not self.users.filter(id=user.id).exists()
        ):
            return False

        if self.for_first_order and user and user.orders.exists():
            return False

        return True

    def apply_discount(self, order_total):
        """Calculate discount amount for the given order total"""
        if self.discount_type == self.DiscountType.PERCENT:
            discount = order_total * (self.discount_value / 100)
            if self.max_discount:
                discount = min(discount, self.max_discount)
            return round(discount, 2)
        else:
            return min(self.discount_value, order_total)


class PromoCodeUse(TimeStampedModel):
    """Track promo code usage"""

    promo_code = models.ForeignKey(
        PromoCode,
        verbose_name=_("promo code"),
        related_name="uses",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("user"),
        related_name="promo_code_uses",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    order = models.ForeignKey(
        "orders.Order",
        verbose_name=_("order"),
        related_name="promo_code_uses",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    discount_amount = models.DecimalField(
        _("discount amount"), max_digits=10, decimal_places=2
    )

    class Meta:
        verbose_name = _("Использование промо кода")
        verbose_name_plural = _("Использование промо кодов")
        ordering = ["-created"]

    def __str__(self):
        return f"{self.promo_code.code} - {self.discount_amount}"
