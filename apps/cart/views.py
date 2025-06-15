from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from apps.products.models import Product
from apps.discounts.models import PromoCode
from .forms import PromoCodeForm
from .models import Cart, CartItem


def cart_detail(request):
    cart = Cart.objects.get_or_create_cart(request)
    return render(
        request, "cart/detail.html", {"cart": cart, "promo_code_form": PromoCodeForm()}
    )


def apply_promo_code(request):
    cart = Cart.objects.get_or_create_cart(request)

    if request.method == "POST":
        promo_code = request.POST.get("promo_code", "").strip()
        remove_promo = "remove_promo" in request.POST

        if remove_promo:
            cart.remove_promo_code()
            messages.success(
                request, _("Promo code removed successfully."), extra_tags="promo_code"
            )
        elif promo_code:
            try:
                promo = PromoCode.objects.get(code=promo_code, active=True)
                if promo.is_valid(
                    request.user if request.user.is_authenticated else None,
                    cart.subtotal,
                ):
                    cart.apply_promo_code(promo)
                    messages.success(
                        request,
                        _("Promo code applied successfully!"),
                        extra_tags="promo_code",
                    )
                else:
                    cart.remove_promo_code()
                    messages.error(
                        request,
                        _("This promo code is not valid for your cart."),
                        extra_tags="promo_code",
                    )
            except PromoCode.DoesNotExist:
                cart.remove_promo_code()
                messages.error(
                    request, _("Invalid promo code."), extra_tags="promo_code"
                )

    return redirect("cart:cart_detail")


@require_POST
def cart_add(request, product_id):
    """Add product to cart or update quantity"""
    cart = Cart.objects.get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={"price": product.price}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, _("Product added to cart"))
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    """Remove product from cart"""
    cart = Cart.objects.get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.items.filter(product=product).delete()
    messages.success(request, _("Product removed from cart"))
    return redirect("cart:cart_detail")


@require_POST
def cart_update(request, product_id):
    """Update product quantity in cart"""
    cart = Cart.objects.get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))

    if quantity <= 0:
        cart.items.filter(product=product).delete()
    else:
        cart_item = cart.items.filter(product=product).first()
        if cart_item:
            cart_item.quantity = quantity
            cart_item.save()

    messages.success(request, _("Cart updated"))
    return redirect("cart:cart_detail")
