# apps/accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import ProfileUpdateForm, CustomPasswordChangeForm
from apps.orders.models import Order
from apps.cart.models import Cart


def customer_register(request):
    """Registration view specifically for shop customers"""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            profile = user.userprofile
            profile.user_type = "customer"
            profile.save()

            session_key = request.session.session_key
            session_cart = None

            if session_key:
                try:
                    session_cart = Cart.objects.get(session_key=session_key)
                except Cart.DoesNotExist:
                    pass

            login(request, user)

            if session_cart and session_cart.has_items():
                user_cart, created = Cart.objects.get_or_create(user=user)
                Cart.objects.merge_carts(session_cart, user_cart)

            messages.success(request, "Регистрация прошла успешно! Добро пожаловать!")

            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url and url_has_allowed_host_and_scheme(
                next_url, request.get_host()
            ):
                return redirect(next_url)

            return redirect("products:category_list")
    else:
        form = UserCreationForm()

    next_url = request.GET.get("next", "")

    context = {
        "form": form,
        "next": next_url,
    }
    return render(request, "accounts/customer_register.html", context)


@login_required
def profile_view(request):
    """View for users to see their profile"""
    profile = request.user.userprofile

    recent_orders = []
    try:
        recent_orders = Order.objects.filter(user=request.user).order_by("-created")[:5]
    except:
        pass

    context = {
        "profile": profile,
        "user": request.user,
        "recent_orders": recent_orders,
    }
    return render(request, "accounts/profile.html", context)


@login_required
def profile_edit(request):
    """View for users to edit their profile"""
    profile = request.user.userprofile

    if request.method == "POST":
        form = ProfileUpdateForm(
            request.POST, request.FILES, instance=profile, user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)

    context = {
        "profile": profile,
        "user": request.user,
        "form": form,
    }

    return render(request, "accounts/profile_edit.html", context)


@login_required
def change_password(request):
    """View for users to change their password"""
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, "Пароль успешно изменен!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки ниже.")
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, "accounts/change_password.html", {"form": form})


@login_required
def orders_list(request):
    """View for users to see all their orders"""
    orders = []
    completed_count = 0
    processing_count = 0

    try:
        orders_queryset = Order.objects.filter(user=request.user).order_by("-created")

        completed_count = orders_queryset.filter(status=Order.Status.COMPLETED).count()
        processing_count = orders_queryset.filter(
            status__in=[
                Order.Status.PROCESSING,
                Order.Status.SHIPPED,
                Order.Status.DELIVERED,
            ]
        ).count()

        paginator = Paginator(orders_queryset, 10)
        page_number = request.GET.get("page")
        orders = paginator.get_page(page_number)
    except:
        messages.info(request, "Система заказов пока недоступна.")

    context = {
        "orders": orders,
        "completed_count": completed_count,
        "processing_count": processing_count,
    }

    return render(request, "accounts/orders_list.html", context)


def user_login(request):
    """Enhanced login view with better redirect handling"""
    if request.user.is_authenticated:
        next_url = request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(next_url, request.get_host()):
            return redirect(next_url)
        return redirect("products:category_list")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            session_key = request.session.session_key
            session_cart = None

            if session_key:
                try:
                    session_cart = Cart.objects.get(session_key=session_key)
                except Cart.DoesNotExist:
                    pass

            login(request, user)

            if session_cart and session_cart.has_items():
                user_cart, created = Cart.objects.get_or_create(user=user)
                Cart.objects.merge_carts(session_cart, user_cart)

            messages.success(
                request, f"Добро пожаловать, {user.first_name or user.username}!"
            )

            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url and url_has_allowed_host_and_scheme(
                next_url, request.get_host()
            ):
                return redirect(next_url)

            return redirect("products:category_list")
        else:
            messages.error(
                request, "Неверные учетные данные. Проверьте имя пользователя и пароль."
            )

    next_url = request.GET.get("next", "")

    context = {
        "next": next_url,
    }
    return render(request, "accounts/login.html", context)


def user_logout(request):
    """Enhanced logout view"""
    username = request.user.username if request.user.is_authenticated else None

    logout(request)

    if username:
        messages.info(request, f"До свидания, {username}! Вы успешно вышли из системы.")
    else:
        messages.info(request, "Вы успешно вышли из системы.")

    return redirect("products:category_list")
