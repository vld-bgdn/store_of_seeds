from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("create/", views.OrderCreateView.as_view(), name="order_create"),
    path("detail/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("cdek-calculate/", views.cdek_calculate_delivery, name="cdek_calculate"),
    path("payment/", views.payment_process, name="payment_process"),
]
