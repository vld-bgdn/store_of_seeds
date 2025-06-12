from django.db import models

# from django.conf import settings
from apps.products.models import Product
from django.utils.translation import gettext_lazy as _


class Cart(models.Model):
    """Session-based cart model"""

    session_key = models.CharField(_("session key"), max_length=40, db_index=True)
    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    class Meta:
        verbose_name = _("cart")
        verbose_name_plural = _("carts")
        ordering = ["-created"]

    def __str__(self):
        return f"Cart {self.pk}"

    @property
    def total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())

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
