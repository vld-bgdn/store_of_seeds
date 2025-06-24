from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.customer_register, name="customer_register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/change-password/", views.change_password, name="change_password"),
    path("profile/orders/", views.orders_list, name="orders_list"),
]
