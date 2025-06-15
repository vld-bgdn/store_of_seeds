from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import JsonResponse

from apps.cart.models import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
from .tasks import order_created


class OrderCreateView(CreateView):
    """View for creating new orders"""

    model = Order
    form_class = OrderCreateForm
    template_name = "orders/order_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get or create cart based on session key
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key

        cart, created = Cart.objects.get_or_create(session_key=session_key)
        context["cart"] = cart
        context["cart_items"] = cart.items.all()  # Add items explicitly

        return context

    def form_valid(self, form):
        # Get cart based on session key
        session_key = self.request.session.session_key
        if not session_key:
            messages.error(self.request, _("No cart found"))
            return redirect("cart:cart_detail")

        try:
            cart = Cart.objects.get(session_key=session_key)
        except Cart.DoesNotExist:
            messages.error(self.request, _("Cart not found"))
            return redirect("cart:cart_detail")

        # Check if cart has items
        if not cart.items.exists():
            messages.error(self.request, _("Your cart is empty"))
            return redirect("cart:cart_detail")

        order = form.save(commit=False)

        if self.request.user.is_authenticated:
            order.user = self.request.user

        order.ip_address = self.request.META.get("REMOTE_ADDR")
        order.delivery_cost = self._calculate_delivery_cost(order.delivery_method, cart)
        order.save()

        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                price=cart_item.price,
                quantity=cart_item.quantity,
            )

        # Clear the cart by deleting all items
        cart.items.all().delete()
        # Or delete the entire cart if you prefer
        # cart.delete()

        # Send order confirmation email asynchronously
        order_created.delay(order.id)

        # Set order in session for payment process
        self.request.session["order_id"] = order.id

        messages.success(self.request, _("Your order has been placed successfully!"))

        return redirect(reverse_lazy("orders:payment_process"))

    def _calculate_delivery_cost(self, delivery_method, cart):
        """Calculate delivery cost based on method"""
        if delivery_method == Order.DeliveryMethod.POST:
            return 200  # Fixed cost for Russian Post
        elif delivery_method == Order.DeliveryMethod.PICKUP:
            return 0
        else:
            # CDEK calculation will be handled via AJAX
            return 0

    def form_valid(self, form):
        cart = Cart(self.request)
        order = form.save(commit=False)

        if self.request.user.is_authenticated:
            order.user = self.request.user

        order.ip_address = self.request.META.get("REMOTE_ADDR")
        order.delivery_cost = self._calculate_delivery_cost(order.delivery_method, cart)

        # Add promo code information
        if cart.promo_code and cart.promo_code_applied:
            order.promo_code = cart.promo_code
            order.discount_amount = cart.discount_amount

        order.save()

        # Create order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                price=item["price"],
                quantity=item["quantity"],
            )

        # Clear the cart
        cart.clear()

        # Send order confirmation email
        order_created.delay(order.id)

        # Set order in session for payment process
        self.request.session["order_id"] = order.id

        messages.success(self.request, _("Your order has been placed successfully!"))

        return redirect(reverse_lazy("orders:payment_process"))


class OrderDetailView(LoginRequiredMixin, DetailView):
    """View for order details"""

    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)


def cdek_calculate_delivery(request):
    """Calculate CDEK delivery cost (mock version)"""
    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        city = request.POST.get("city")
        cart_total = float(request.POST.get("cart_total", 0))

        # Mock calculation - in real app this would call CDEK API
        if city and cart_total:
            # Simple mock logic - adjust as needed
            base_cost = 300
            if cart_total > 2000:
                base_cost = 200
            elif cart_total > 5000:
                base_cost = 0  # Free delivery for large orders

            return JsonResponse(
                {
                    "success": True,
                    "cost": base_cost,
                    "points": [
                        {"id": "1", "address": "ул. Примерная, 1, Москва"},
                        {"id": "2", "address": "ул. Тестовая, 5, Москва"},
                    ],
                }
            )

    return JsonResponse({"success": False, "error": "Invalid request"})


def payment_process(request):
    """Process payment (mock version for Yandex Pay)"""
    order_id = request.session.get("order_id")
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        # In a real app, this would verify payment with Yandex Pay API
        order.payment_status = Order.PaymentStatus.PAID
        order.save()

        # Clear the order from session
        if "order_id" in request.session:
            del request.session["order_id"]

        return render(request, "orders/payment_done.html", {"order": order})

    return render(request, "orders/payment_process.html", {"order": order})
