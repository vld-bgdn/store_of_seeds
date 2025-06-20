from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("create/", views.OrderCreateView.as_view(), name="order_create"),
    path("detail/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("cdek-calculate/", views.cdek_calculate_delivery, name="cdek_calculate"),
    path("payment/", views.payment_process, name="payment_process"),
    path("order/<int:order_id>/pay/", views.create_payment, name="create_payment"),
    path("payment/webhook/", views.yookassa_webhook, name="payment_webhook"),
    path(
        "payment/success/<int:order_id>/", views.payment_success, name="payment_success"
    ),
    path(
        "payment/failed/<int:order_id>/", views.payment_failure, name="payment_failure"
    ),
]
