from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from apps.products.models import Product
from .models import Cart, CartItem


def get_or_create_cart(request):
    """Get or create cart based on session key"""
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


@require_POST
def cart_add(request, product_id):
    """Add product to cart or update quantity"""
    cart = get_or_create_cart(request)
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
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.items.filter(product=product).delete()
    messages.success(request, _("Product removed from cart"))
    return redirect("cart:cart_detail")


def cart_detail(request):
    """Display cart contents"""
    cart = get_or_create_cart(request)
    return render(request, "cart/detail.html", {"cart": cart})


@require_POST
def cart_update(request, product_id):
    """Update product quantity in cart"""
    cart = get_or_create_cart(request)
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
