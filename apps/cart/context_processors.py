from .models import Cart


def cart_context(request):
    """Add cart to template context for all views"""
    cart = Cart.objects.get_or_create_cart(request)
    return {"cart": cart}
