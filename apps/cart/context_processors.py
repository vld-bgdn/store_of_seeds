from .models import Cart


def cart(request):
    """Add cart to template context"""
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return {"cart": cart}
