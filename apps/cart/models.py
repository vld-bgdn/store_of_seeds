from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product
from apps.discounts.models import PromoCode, PromoCodeUse
from django.utils.translation import gettext_lazy as _


class CartManager(models.Manager):
    def get_or_create_cart(self, request):
        if request.user.is_authenticated:

            cart, created = self.get_or_create(user=request.user)
            return cart
        else:

            if not request.session.session_key:
                request.session.create()
            cart, created = self.get_or_create(session_key=request.session.session_key)
            return cart

    def merge_carts(self, session_cart, user_cart):
        """Merge session cart into user cart"""
        for session_item in session_cart.items.all():
            user_item, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=session_item.product,
                defaults={
                    "quantity": session_item.quantity,
                    "price": session_item.price,
                },
            )

            if not created:
                user_item.quantity += session_item.quantity
                user_item.save()

        if session_cart.promo_code and not user_cart.promo_code:
            user_cart.promo_code = session_cart.promo_code
            user_cart.promo_code_applied = session_cart.promo_code_applied
            user_cart.save()

        session_cart.clear()
        session_cart.delete()


class Cart(models.Model):
    user = models.OneToOneField(
        User, verbose_name=_("user"), on_delete=models.CASCADE, null=True, blank=True
    )
    session_key = models.CharField(
        _("session key"), max_length=40, db_index=True, null=True, blank=True
    )
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

        if self.user:
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

        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(user__isnull=False),
                name="unique_user_cart",
            ),
            models.UniqueConstraint(
                fields=["session_key"],
                condition=models.Q(session_key__isnull=False),
                name="unique_session_cart",
            ),
        ]

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart {self.pk} (session: {self.session_key})"

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

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

    def clear(self):
        """Clear all items and promo code from cart"""
        self.items.all().delete()
        self.promo_code = None
        self.promo_code_applied = False
        self.save()

    def has_items(self):
        """Check if cart has any items"""
        return self.items.exists()


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

    @property
    def total_price(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = _("cart item")
        verbose_name_plural = _("cart items")
        unique_together = [["cart", "product"]]

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
