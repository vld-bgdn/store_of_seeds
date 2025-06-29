# apps/orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import REDIRECT_FIELD_NAME
from yookassa import Configuration, Payment, Webhook
import uuid
import json

from apps.cart.models import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm

from .tasks import order_created, payment_received


class OrderCreateView(LoginRequiredMixin, CreateView):
    """
    Order creation view - requires authentication
    Redirects anonymous users to login page
    """

    model = Order
    form_class = OrderCreateForm
    template_name = "orders/order_create.html"
    login_url = "accounts:login"
    redirect_field_name = REDIRECT_FIELD_NAME

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to check if cart has items before allowing order creation
        """
        if not request.user.is_authenticated:

            messages.info(
                request,
                _(
                    "Для оформления заказа необходимо войти в систему или зарегистрироваться."
                ),
            )
            return super().dispatch(request, *args, **kwargs)

        cart = Cart.objects.get_or_create_cart(request)
        if not cart.has_items():
            messages.warning(
                request, _("Ваша корзина пуста. Добавьте товары для оформления заказа.")
            )
            return redirect("cart:cart_detail")

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["cart"] = Cart.objects.get_or_create_cart(self.request)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart.objects.get_or_create_cart(self.request)
        context["cart"] = cart
        context["delivery_cost"] = self._calculate_delivery_cost(
            self.request.POST.get("delivery_method", Order.DeliveryMethod.POST), cart
        )
        return context

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
        cart = Cart.objects.get_or_create_cart(self.request)

        if not self.request.user.is_authenticated:
            messages.error(
                self.request, _("Для оформления заказа необходимо войти в систему.")
            )
            return redirect("accounts:login")

        if not cart.has_items():
            messages.warning(self.request, _("Ваша корзина пуста."))
            return redirect("cart:cart_detail")

        order = form.save(commit=False)
        order.user = self.request.user
        order.delivery_cost = self._calculate_delivery_cost(order.delivery_method, cart)

        if cart.promo_code and cart.promo_code_applied:
            order.promo_code = cart.promo_code
            order.discount_amount = cart.discount_amount

        order.save()

        # Create order items
        for cart_item in cart.items.select_related("product").all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                price=cart_item.price,
                quantity=cart_item.quantity,
            )

        order.total_cost = order.calculate_total()
        order.save()

        cart.clear()

        order_created.delay(order.id)

        self.request.session["order_id"] = order.id

        messages.success(self.request, _("Ваш заказ успешно оформлен!"))
        return redirect(reverse_lazy("orders:payment_process"))


class OrderDetailView(LoginRequiredMixin, DetailView):
    """View for order details - requires authentication"""

    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"
    login_url = "accounts:login"

    def get_queryset(self):
        """Only allow users to see their own orders (staff can see all)"""
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


@login_required
def payment_process(request):
    """Process payment - requires authentication"""
    order_id = request.session.get("order_id")
    if not order_id:
        messages.error(request, _("Заказ не найден."))
        return redirect("cart:cart_detail")

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        order.payment_status = Order.PaymentStatus.PAID
        order.save()

        if "order_id" in request.session:
            del request.session["order_id"]

        return render(request, "orders/payment_done.html", {"order": order})

    return render(request, "orders/payment_process.html", {"order": order})


@login_required
def create_payment(request, order_id):
    """Process payment in Yookassa - requires authentication"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    payment = Payment.create(
        {
            "amount": {
                "value": str(order.calculate_total()),
                "currency": "RUB",
            },
            "confirmation": {
                "type": "redirect",
                "return_url": request.build_absolute_uri(
                    reverse(settings.YOOKASSA_SUCCESS_URL, args=[order.id])
                ),
            },
            "capture": True,
            "description": f"Order #{order.id}",
            "metadata": {
                "order_id": order.id,
                "user_id": request.user.id,
            },
            "idempotency_key": str(uuid.uuid4()),
        }
    )

    order.payment_id = payment.id
    order.payment_status = "pending"
    order.payment_data = payment.json()
    order.save()

    return redirect(payment.confirmation.confirmation_url)


@csrf_exempt
def yookassa_webhook(request):
    """Webhook handler for Yookassa payments"""
    if request.method != "POST":
        return HttpResponse(status=405)

    try:
        event_data = json.loads(request.body)

        if hasattr(settings, "YOOKASSA_WEBHOOK_AUTH_KEY"):
            signature = request.headers.get("Content-Signature", "")
            if not Webhook().is_valid_signature(
                request.body, signature, settings.YOOKASSA_WEBHOOK_AUTH_KEY
            ):
                return HttpResponse(status=400)

        if event_data["event"] == "payment.succeeded":
            payment = event_data["object"]
            order = Order.objects.get(id=payment["metadata"]["order_id"])
            order.payment_status = "succeeded"
            order.paid_at = payment.get("captured_at") or payment.get("created_at")
            order.save()

            payment_received.delay(order.id)

        elif event_data["event"] == "payment.canceled":
            payment = event_data["object"]
            order = Order.objects.get(id=payment["metadata"]["order_id"])
            order.payment_status = "canceled"
            order.save()

        return JsonResponse({"status": "ok"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def payment_success(request, order_id):
    """Payment success handler - requires authentication"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.payment_id and order.payment_status == "pending":
        payment = Payment.find_one(order.payment_id)

        if payment.status == "succeeded":
            order.payment_status = "succeeded"
            order.paid_at = payment.captured_at or payment.created_at
            order.save()
        elif payment.status == "canceled":
            return redirect("orders:payment_failure", order_id=order.id)

    if order.payment_status != "succeeded":
        return redirect("orders:payment_failure", order_id=order.id)

    return render(request, "orders/payment_success.html", {"order": order})


@login_required
def payment_failure(request, order_id):
    """Payment failure handler - requires authentication"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/payment_failure.html", {"order": order})
