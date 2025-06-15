from django.db import models

# from django.conf import settings
from apps.products.models import Product
from apps.discounts.models import PromoCode, PromoCodeUse
from django.utils.translation import gettext_lazy as _


class CartManager(models.Manager):
    def get_or_create_cart(self, request):
        if not request.session.session_key:
            request.session.create()
        cart, created = self.get_or_create(session_key=request.session.session_key)
        return cart


class Cart(models.Model):
    session_key = models.CharField(_("session key"), max_length=40, db_index=True)
    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)
    promo_code = models.ForeignKey(
        PromoCode,
        verbose_name=_("promo code"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    promo_code_applied = models.BooleanField(_("promo code applied"), default=False)

    objects = CartManager()

    def apply_promo_code(self, promo_code):
        self.promo_code = promo_code
        self.promo_code_applied = True
        self.save()

        # Increment promo code usage if user is authenticated
        if hasattr(self, "user") and self.user:
            PromoCodeUse.objects.create(
                promo_code=promo_code,
                user=self.user,
                discount_amount=self.discount_amount,
            )
            promo_code.current_uses += 1
            promo_code.save(update_fields=["current_uses"])

    def remove_promo_code(self):
        self.promo_code = None
        self.promo_code_applied = False
        self.save()

    class Meta:
        verbose_name = _("cart")
        verbose_name_plural = _("carts")
        ordering = ["-created"]

    def __str__(self):
        return f"Cart {self.pk}"

    @property
    def subtotal(self):
        return sum(item.price * item.quantity for item in self.items.all())

    @property
    def discount_amount(self):
        if self.promo_code and self.promo_code_applied:
            return self.promo_code.apply_discount(self.subtotal)
        return 0

    @property
    def total(self):
        return self.subtotal - self.discount_amount

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Items in the cart"""

    cart = models.ForeignKey(
        Cart, verbose_name=_("cart"), related_name="items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, verbose_name=_("product"), on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(_("quantity"), default=1)
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("cart item")
        verbose_name_plural = _("cart items")
        unique_together = [["cart", "product"]]

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def total_price(self):
        return self.price * self.quantity
