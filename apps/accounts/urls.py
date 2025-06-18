from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.customer_register, name="customer_register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.profile_view, name="profile"),
]
